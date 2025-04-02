import httpx
from tabpfn_common_utils.usage_analytics.analytics_definition import ANALYTICS_TO_TRACK


class AnalyticsHttpClient(httpx.Client):
    """
    Custom HTTP client that automatically adds the calling class to all requests.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if headers is None:
            headers = {}

        # Add the analytics headers
        for header_name, get_value_func in ANALYTICS_TO_TRACK:
            headers[header_name] = get_value_func()

        kwargs["headers"] = headers

        # Call the original request method
        return super().request(method, url, *args, **kwargs)
