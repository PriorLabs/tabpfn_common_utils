import unittest
from unittest.mock import patch, MagicMock
import httpx
from usage_analytics import AnalyticsHttpClient, ANALYTICS_HEADER_CONFIG


class TestAnalyticsHttpClient(unittest.TestCase):
    def setUp(self) -> None:
        self.module_name = "test_module"
        self.client = AnalyticsHttpClient(module_name=self.module_name)
        self.local_host = "http://localhost:8000"

    def test_init(self):
        """Test that the client initializes with the correct module name."""
        self.assertEqual(self.client.module_name, self.module_name)
        self.assertIsInstance(self.client, httpx.Client)

    @patch("usage_analytics.analytics_http_client.super")
    def test_request_adds_headers(self, mock_super: MagicMock):
        """Test that request method adds analytics headers."""
        mock_request = MagicMock()
        mock_super.return_value.request = mock_request

        # Call request method
        self.client.request("GET", self.local_host)

        # Check that super().request was called with modified headers
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], self.local_host)

        # Verify headers were added
        headers = kwargs.get("headers", {})
        self._validate_headers(headers)

    @patch("usage_analytics.analytics_http_client.super")
    def test_stream_adds_headers(self, mock_super):
        """Test that stream method adds analytics headers."""
        mock_stream = MagicMock()
        mock_super.return_value.stream = mock_stream

        # Call stream method
        self.client.stream("GET", self.local_host)

        # Check that super().stream was called with modified headers
        args, kwargs = mock_stream.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], self.local_host)

        # Verify headers were added
        headers = kwargs.get("headers", {})
        self._validate_headers(headers)

    def _validate_headers(self, headers: dict) -> None:
        for header_name, _ in ANALYTICS_HEADER_CONFIG:
            self.assertIn(header_name, headers)
            self.assertIsNotNone(headers.get(header_name))

    def test_set_module_name(self):
        """Test that the module name can be updated."""
        new_module_name = "new_test_module"
        self.client.set_module_name(new_module_name)

        with patch("usage_analytics.analytics_http_client.super") as mock_super:
            mock_request = MagicMock()
            mock_super.return_value.request = mock_request

            self.client.request("GET", self.local_host)

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})

            self.assertEqual(headers.get("PL-Module-Name"), new_module_name)
            self.assertEqual(self.client.module_name, new_module_name)


if __name__ == "__main__":
    unittest.main()
