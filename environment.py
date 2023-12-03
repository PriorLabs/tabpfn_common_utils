import typing
import logging

from tabpfn_common_utils.utils import singleton

logger = logging.getLogger(__name__)


@singleton
class EnvironmentInstance(dict):
    """
    EnvironmentInstance is a singleton class that serves to store the execution env. of the current process.
    It is a subclass of dict, so it can be used as a dict to store any global variables that are needed by multiple
    modules.
    """

    def __init__(self, mode: typing.Literal["dev", "test", "prod"]):
        super().__init__()
        self["mode"] = mode


class Environment:
    """
    A wrapper class for EnvironmentInstance. It provides static methods to initialize, reset, and get the
    EnvironmentInstance. This offers a safer way to access EnvironmentInstance, as it handles the case where the
    EnvironmentInstance has been deleted.

    Usage:
        # handle reset (deletion) of EnvironmentInstance
        Environment.init(mode="dev")
        Environment.add_property(a=1, b=2)
        Environment.get_property() # returns {"mode": "dev", "a": 1, "b": 2}
        Environment.reset()
        Environment.get_property() # raises RuntimeError

        # prevent the creation Environment instance with different mode
        Environment.init(mode="dev")
        Environment.init(mode="test") # raises RuntimeError
    """

    _instance = None

    @staticmethod
    def init(mode):
        if Environment._instance is not None and Environment._instance["mode"] != mode:
            raise RuntimeError(
                f"Environment of mode {Environment._instance['mode']} already exists. "
                f"Cannot create Environment instance with different mode."
            )
        Environment._instance = EnvironmentInstance(mode)
        logger.info(f"Environment {Environment._instance}")

    @staticmethod
    def reset():
        if Environment._instance is not None:
            Environment._instance.delete_instance()
            Environment._instance = None

    @staticmethod
    def get_property():
        if Environment._instance is None:
            raise RuntimeError("Environment has not been initialized.")

        return Environment._instance

    @staticmethod
    def add_property(**kwargs):
        if Environment._instance is None:
            raise RuntimeError("Environment has not been initialized.")

        for key, value in kwargs.items():
            Environment._instance[key] = value
