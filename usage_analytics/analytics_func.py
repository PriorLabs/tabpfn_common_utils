import inspect
import platform
import uuid


def get_calling_class(recursive=True) -> str:
    """
    Traverses the call stack to find and return the class name of the first
    caller that has a 'self' variable in its frame (i.e., a method call).
    If no such frame is found, returns 'StandaloneFunction'.
    """

    # Skip the current frame and the immediate caller (i.e., start from index 1)
    stack = inspect.stack()[1:]

    outermost_caller = "StandaloneFunction"  # Default return value

    for frame_record in stack:
        frame = frame_record.frame
        # Look for 'self' in the frame's local variables
        self_obj = frame.f_locals.get("self", None)
        if self_obj is not None:
            # Return the class name of the 'self' instance
            outermost_caller = type(self_obj).__name__
            if not recursive:
                break

    return outermost_caller


def get_python_version() -> str:
    return platform.python_version()


def get_unique_call_id() -> str:
    return str(uuid.uuid4())
