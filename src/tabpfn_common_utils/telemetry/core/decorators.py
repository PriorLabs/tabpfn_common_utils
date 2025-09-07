"""Decorators for recording model calls."""

from __future__ import annotations

import functools
import inspect
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Literal

from .events import FitEvent, PredictEvent
from .service import capture_event
from tabpfn_common_utils.utils import shape_of

# Logger
logger = logging.getLogger(__name__)

# Type of model tasks
ModelTaskType = Literal["classification", "regression"]
ModelMethodType = Literal["fit", "predict"]

# Event resolver
_EVENT_BY_METHOD: dict[ModelMethodType, type[FitEvent] | type[PredictEvent]] = {
    "fit": FitEvent,
    "predict": PredictEvent,
}


def track_model_call(model_method: ModelMethodType, param_names: list[str]) -> Callable:
    """Decorator that tracks model calls.

    Args:
        model_method: Model execution method, `fit` or `predict`.
        param_names: List of parameters to track for.

    Example:
        @track_model_call(model_method="fit", param_names=["X_test", ...])
        def prepare(...):
    """

    def decorator(func: Callable) -> Callable:
        # Validate parameter names at decoration time
        signature = inspect.signature(func)

        func_param_names = set(signature.parameters.keys())
        for param_name in param_names:
            if param_name not in func_param_names:
                raise ValueError(f"Parameter {param_name} not declared")

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _safe_call_with_telemetry(
                func, args, kwargs, model_method, param_names
            )

        return wrapper

    return decorator


def _safe_call_with_telemetry(
    func: Callable,
    args: tuple,
    kwargs: dict,
    model_method: ModelMethodType,
    param_names: list[str],
) -> Any | None:
    """Execute function with telemetry, handling all exceptions internally.

    Args:
        func: The function to execute, decorated.
        args: Positional arguments.
        kwargs: Keyword arguments.
        model_method: Model execution method.
        param_names: List of parameters to track for.

    Returns:
        Tuple of (result, call_info).
    """
    call_info = None

    # Step 1: Pick up call information using introspection
    try:
        call_info = _make_callinfo(
            func,
            model_method,
            param_names,
            *args,
            **kwargs,
        )
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Call info failed with: {e}")

    # Step 2: Run the actual function
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration_ms = int((time.perf_counter() - start) * 1000)

    # Step 3: Send telemetry event
    if call_info is not None:
        try:
            _send_model_called_event(call_info, duration_ms)
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Telemetry failed for {func.__name__}: {e}")

    return result


def _send_model_called_event(call_info: _ModelCallInfo, duration_ms: int) -> None:
    """Send telemetry event for a model call.

    Args:
        call_info: Call information.
        duration_ms: Duration in milliseconds.
    """
    # Task (regression | classification) is required
    if call_info.task is None:
        return

    # Infer event type and dimensionality
    _event_cls = _EVENT_BY_METHOD.get(call_info.model_method)
    if not _event_cls or len(call_info.shapes) < 1:
        return

    # Build event
    num_rows, num_columns = _extract_shape_info(call_info.shapes)
    event_kwargs = {
        "task": call_info.task,
        "num_rows": num_rows,
        "num_columns": num_columns,
        "duration_ms": duration_ms,
    }

    # Create event, might fail due to a type mismatch
    try:
        event = _event_cls(**event_kwargs)
    except TypeError as e:
        logger.debug(f"Event creation failed: {e}")
        return

    # Send event, catch all backend exceptions
    try:
        capture_event(event)
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Event capture failed: {e}")
        return


def _extract_shape_info(shapes: dict[str, tuple[int, ...]]) -> tuple[int, int]:
    """Extract total samples and features from shapes dictionary.

    Args:
        shapes: Dictionary of parameter names to their shapes

    Returns:
        Tuple of (num_rows, num_columns)
    """
    num_rows, num_columns = 0, 0
    for shape in shapes.values():
        if len(shape) >= 2 and shape[1] > 1:  # X data: (samples, features)
            num_rows += shape[0]
            num_columns += shape[1]
        elif len(shape) == 1:  # y data: (samples,)
            num_rows += shape[0]
    return num_rows, num_columns


@dataclass
class _StackFrame:
    """A single frame in the call stack."""

    function_name: str | None
    module_name: str | None


@dataclass
class _ModelCallInfo:
    """Info about a decorated model call, its arguments and call stack."""

    shapes: dict[str, tuple[int, ...]]
    task: Literal["classification", "regression"]
    model_method: Literal["fit", "predict"]


def _capture_call_stack(func: Callable, max_frames: int = 25) -> list[_StackFrame]:
    """Capture the call stack for a model call function.

    Args:
        func: The function to capture the call stack for.
        max_frames: The maximum number of frames to capture.

    Returns:
        The call stack.
    """
    frames: list[_StackFrame] = []

    # Capture the decorated function's module and file
    func_mod = getattr(func, "__module__", None)
    frame = _StackFrame(getattr(func, "__name__", None), func_mod)
    frames.append(frame)

    f = inspect.currentframe()

    # Skip internal functions
    internal = {"_capture_call_stack", "_make_callinfo", "wrapper", "track_model_call"}
    while f and f.f_code.co_name in internal:
        f = f.f_back

    # Capture the call stack
    while f and len(frames) < max_frames:
        # Skip internal functions
        if f.f_code.co_name in internal:
            f = f.f_back
            continue

        # Get the module name
        m = inspect.getmodule(f)
        mod_name = m.__name__ if m else f.f_globals.get("__name__")

        frame = _StackFrame(f.f_code.co_name, mod_name)
        frames.append(frame)

        # Move to the next frame
        f = f.f_back

    return frames


def _make_callinfo(
    func: Callable,
    model_method: ModelMethodType,
    param_names: list[str],
    *args: Any,
    **kwargs: Any,
) -> _ModelCallInfo | None:
    """Collect model call information.

    Args:
        func: Called and decorated function.
        *args: Positional input arguments.
        **kwargs: Keyword arguments for the function.
        model_method: Model execution method.
        param_names: List of parameters to track for.
    """
    # Get the function signature
    sig = inspect.signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()

    # Capture stack and infer the task from it
    stack = _capture_call_stack(func)

    # Infer the model task from the call stack.
    task = _infer_task(stack)
    if task is None:
        return None

    # Get the shapes based on tracked params
    shapes: dict[str, tuple[int, ...]] = {}
    for param_name in param_names:
        if param_name in bound.arguments:
            shape = shape_of(bound.arguments[param_name])
            if shape is not None:
                shapes[param_name] = shape

    return _ModelCallInfo(shapes=shapes, task=task, model_method=model_method)


def _infer_task(stack: list[_StackFrame]) -> ModelTaskType | None:
    """Infer the model task from the call stack."""
    for frame in stack:
        m = frame.module_name or ""
        if m.startswith("tabpfn.classifier"):
            return "classification"
        if m.startswith("tabpfn.regressor"):
            return "regression"
    return None
