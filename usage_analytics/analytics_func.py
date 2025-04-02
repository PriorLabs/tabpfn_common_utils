def get_calling_class(recursive=True):
    """
    Traverses the call stack to find and return the class name of the first
    caller that has a 'self' variable in its frame (i.e., a method call).
    If no such frame is found, returns 'StandaloneFunction'.
    """

    import inspect

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

    # If no class context was found, assume it's a standalone function
    return outermost_caller


def get_python_version():
    import platform

    return platform.python_version()


def get_unique_call_id():
    import uuid

    return str(uuid.uuid4())


# Example usage in a class method:
class ExampleCaller:
    def call_api(self):
        # This function would call the API and use get_calling_class to report the caller
        caller_class = get_calling_class()
        print(f"Called from class: {caller_class}")


class NestedExampleCaller:
    def __init__(self):
        self.example_caller = ExampleCaller()

    def call_api(self):
        self.example_caller.call_api()


def standalone_function():
    # This function doesn't belong to any class, so it should return "StandaloneFunction"
    caller_class = get_calling_class()
    print(f"Called from: {caller_class}")


if __name__ == "__main__":
    # Test the get_calling_class function
    example = ExampleCaller()
    example.call_api()  # Expected output: Called from class: ExampleCaller
    nested_example = NestedExampleCaller()
    nested_example.call_api()  # Expected output: Called from class: NestedExampleCaller
    standalone_function()  # Expected output: Called from: StandaloneFunction

    # Test the get_python_ver function
    print(f"Python version: {get_python_version()}")
