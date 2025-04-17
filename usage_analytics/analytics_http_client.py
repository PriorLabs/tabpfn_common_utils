import httpx
from typing import Callable

from .analytics_config import ANALYTICS_HEADER_CONFIG, ANALYTICS_KEYS


class AnalyticsHttpClient(httpx.Client):
    """
    Custom HTTP client that extends httpx.Client to automatically add analytics headers to all requests.
    """

    def __init__(
        self,
        module_name: str,
        analytics_config: tuple[tuple[str, Callable], ...] = ANALYTICS_HEADER_CONFIG,
        *args,
        **kwargs,
    ):
        """
        Initialize the AnalyticsHttpClient with analytics headers.

        Parameters
        ----------
        module_name : str
            The name of the module using this client, added to analytics headers.
        analytics_config : tuple[tuple[str, Callable], ...], optional
            Configuration for analytics headers, defaults to ANALYTICS_HEADER_CONFIG.
            Each entry is a tuple of (header_name, get_value_func) where get_value_func
            is a callable that returns the value for the header.
        """

        super().__init__(*args, **kwargs)
        self._module_name = module_name
        self._analytics_config = analytics_config

    @property
    def module_name(self) -> str:
        return self._module_name

    def set_module_name(self, module_name: str) -> None:
        self._module_name = module_name

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if headers is None:
            headers = {}

        new_kwargs = {**kwargs, "headers": self._add_analytics_headers(headers)}

        return super().request(method, url, *args, **new_kwargs)

    def stream(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if headers is None:
            headers = {}

        new_kwargs = {**kwargs, "headers": self._add_analytics_headers(headers)}

        return super().stream(method, url, *args, **new_kwargs)

    def _add_analytics_headers(self, headers: dict) -> dict:
        for header_name, get_value_func in self._analytics_config:
            if header_name == ANALYTICS_KEYS.ModuleName:
                headers[header_name] = self._module_name
            elif get_value_func is not None:
                headers[header_name] = get_value_func()
            else:
                raise ValueError(
                    f"Invalid analytics config: header_name={header_name}, get_value_func={get_value_func}"
                )
        return headers
