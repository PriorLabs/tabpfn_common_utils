def singleton(cls):
    """
    Decorator to make a class a singleton.

    Args:
        cls: The class to make a singleton.

    Returns:
        The singleton instance of the class.
    """
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper
