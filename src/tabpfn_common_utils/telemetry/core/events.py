import os
import platform
import sys
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Literal, Optional
from .runtime import get_runtime


def _uuid4() -> str:
    """
    Generate a random UUID4.

    Returns:
        str: UUID4 as a string.
    """
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    """
    Get the current UTC date and time.

    Returns:
        datetime: Current UTC date and time.
    """
    return datetime.now(timezone.utc)


@lru_cache(maxsize=1)
def _get_py_version() -> str:
    """
    Get the Python version as a string.

    Returns:
        str: Python version (e.g., "3.9")
    """
    version_info = sys.version_info
    return f"{version_info.major}.{version_info.minor}"


@lru_cache(maxsize=1)
def _get_sdk_version() -> str:
    """
    Get the version of the tabpfn package if it's installed.

    Returns:
        str: Version string if tabpfn is installed.
    """
    return _get_package_version("tabpfn")


@lru_cache(maxsize=1)
def _get_torch_version() -> str:
    """Get the version of the PyTorch library if it's installed.

    Returns:
        str: Version string if PyTorch is installed.
    """
    return _get_package_version("torch")


@lru_cache(maxsize=1)
def _get_sklearn_version() -> str:
    """Get the version of the scikit-learn library if it's installed.

    Returns:
        str: Version string if scikit-learn is installed.
    """
    return _get_package_version("sklearn")


@lru_cache(maxsize=1)
def _get_numpy_version() -> str:
    """Get the version of the NumPy library if it's installed.

    Returns:
        str: Version string if NumPy is installed.
    """
    return _get_package_version("numpy")


@lru_cache(maxsize=1)
def _get_pandas_version() -> str:
    """Get the version of the Pandas library if it's installed.

    Returns:
        str: Version string if Pandas is installed.
    """
    return _get_package_version("pandas")


@lru_cache(maxsize=1)
def _get_autogluon_version() -> str:
    """Get the version of the AutoGluon library if it's installed.

    Returns:
        str: Version string if AutoGluon is installed.
    """
    return _get_package_version("autogluon.core")


@lru_cache(maxsize=None)
def _get_gpu_type() -> Optional[str]:
    """Detect a local GPU using PyTorch (the TabPFN dependency) and return its
    human-readable name.

    Returns:
        Optional[str]: Human-readable name of the GPU if available.
    """
    try:
        import torch  # type: ignore[import]
    except ImportError:
        return None

    try:
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            return name or "unknown"

    except Exception:  # noqa: BLE001
        pass

    # Apple Silicon via MPS
    try:
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # torch doesn't expose an MPS "model string"
            return "Apple M-series GPU (MPS)"
    except Exception:
        pass

    return None


def _get_package_version(package_name: str) -> str:
    """Get the version of a package if it's installed.

    Args:
        package_name: Name of the package to import (e.g., "torch", "tabpfn").

    Returns:
        str: Version string if the package is installed, "unknown" otherwise.
    """
    try:
        import importlib

        module = importlib.import_module(package_name)  # type: ignore[import]
        return getattr(module, "__version__", "unknown")
    except ImportError:
        return "unknown"


@lru_cache(maxsize=1)
def _get_platform_os() -> str:
    """Get the operating system of the platform.

    Returns:
        str: Operating system of the platform.
    """
    return platform.system()


@lru_cache(maxsize=1)
def _get_runtime_kernel() -> Optional[str]:
    """Get the runtime environment of the platform.

    Returns:
        str: Runtime environment of the platform.
    """
    runtime = get_runtime()
    return runtime.kernel


@dataclass
class BaseTelemetryEvent:
    """
    Base class for all telemetry events.
    """

    # Python version that the SDK is running on
    python_version: str = field(default_factory=_get_py_version, init=False)

    # TabPFN version that the SDK is running on
    tabpfn_version: str = field(default_factory=_get_sdk_version, init=False)

    # Timestamp of the event
    timestamp: datetime = field(default_factory=_utc_now, init=False)

    # Name of the TabPFN extension making the call
    extension: Optional[str] = field(default=None, init=False)

    # Runtime environment of the platform
    runtime_kernel: Optional[str] = field(
        default_factory=_get_runtime_kernel, init=False
    )

    # Operating system of the platform
    platform_os: str = field(default_factory=_get_platform_os, init=False)

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def source(self) -> str:
        return os.environ.get("TABPFN_TELEMETRY_SOURCE", "sdk")

    @property
    def properties(self) -> dict[str, Any]:
        d = asdict(self)
        d["source"] = self.source
        d.pop("timestamp", None)
        d.pop("name", None)
        return d


@dataclass
class PingEvent(BaseTelemetryEvent):
    """
    Event emitted when a ping is sent.
    """

    frequency: Literal["daily", "weekly", "monthly"] = "daily"

    @property
    def name(self) -> str:
        return "ping"


@dataclass
class DatasetEvent(BaseTelemetryEvent):
    """
    Event emitted when a dataset is loaded. No data is sent with this event.
    """

    # Task associated with the dataset
    task: Literal["classification", "regression"]

    # Role of the dataset in the training/testing process
    role: Literal["train", "test"]

    # Number of rows in the dataset
    num_rows: int = 0

    # Number of columns in the dataset
    num_columns: int = 0

    @property
    def name(self) -> str:
        return "dataset"


@dataclass
class ModelCallEvent(BaseTelemetryEvent):
    """
    Base class for events emitted when a model method is called (fit or predict).
    """

    # Task associated with the model call
    task: Literal["classification", "regression"]

    # Version of the PyTorch
    torch_version: str = field(default_factory=_get_torch_version, init=False)

    # Version of the scikit-learn
    sklearn_version: str = field(default_factory=_get_sklearn_version, init=False)

    # Version of the NumPy
    numpy_version: str = field(default_factory=_get_numpy_version, init=False)

    # Version of the Pandas
    pandas_version: str = field(default_factory=_get_pandas_version, init=False)

    # Version of the AutoGluon
    autogluon_version: str = field(default_factory=_get_autogluon_version, init=False)

    # Type of GPU if available
    gpu_type: Optional[str] = field(default_factory=_get_gpu_type, init=False)

    # Version of the model
    model_version: Optional[str] = field(default=None, init=False)

    # Path to the model
    model_path: Optional[str] = field(default=None, init=False)

    # Number of rows in the dataset
    num_rows: int = 0

    # Number of columns in the dataset
    num_columns: int = 0

    # Duration of the model call in milliseconds
    duration_ms: int = -1


@dataclass
class FitEvent(ModelCallEvent):
    """
    Event emitted when a model is fit.
    """

    @property
    def name(self) -> str:
        return "fit_called"


@dataclass
class PredictEvent(ModelCallEvent):
    """
    Event emitted when a model is used to make predictions.
    """

    @property
    def name(self) -> str:
        return "predict_called"
