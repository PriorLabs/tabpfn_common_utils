import unittest
from unittest.mock import patch, MagicMock
import http
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
        self.assertEqual(args[0], http.RequestMethod.GET)
        self.assertEqual(args[1], self.local_host)

        # Verify headers were added
        headers = kwargs.get("headers", {})
        self._validate_headers(headers)

    def _validate_headers(self, headers: dict) -> None:
        for header_name, _ in ANALYTICS_HEADER_CONFIG:
            self.assertIn(header_name, headers)
            self.assertIsNotNone(headers.get(header_name))

    @patch("usage_analytics.analytics_func.get_unique_call_id")
    def test_unique_call_id_header(self, mock_get_unique_call_id):
        """Test that the unique call ID is correctly added to headers."""
        mock_unique_id = "test-unique-id-123"
        mock_get_unique_call_id.return_value = mock_unique_id

        with patch("usage_analytics.analytics_http_client.super") as mock_super:
            mock_request = MagicMock()
            mock_super.return_value.request = mock_request

            self.client.request("GET", self.local_host)

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})

            self.assertEqual(headers.get("PL-Unique-Call-Id"), mock_unique_id)
            mock_get_unique_call_id.assert_called_once()

    @patch("usage_analytics.analytics_func.get_python_version")
    def test_python_version_header(self, mock_get_python_version):
        """Test that the Python version is correctly added to headers."""
        mock_python_version = "3.9.0"
        mock_get_python_version.return_value = mock_python_version

        with patch("usage_analytics.analytics_http_client.super") as mock_super:
            mock_request = MagicMock()
            mock_super.return_value.request = mock_request

            self.client.request("GET", self.local_host)

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})

            self.assertEqual(headers.get("PL-Python-Version"), mock_python_version)
            mock_get_python_version.assert_called_once()

    @patch("usage_analytics.analytics_func.get_calling_class")
    def test_calling_class_header(self, mock_get_calling_class):
        """Test that the calling class is correctly added to headers."""
        mock_calling_class = "TestClass"
        mock_get_calling_class.return_value = mock_calling_class

        with patch("usage_analytics.analytics_http_client.super") as mock_super:
            mock_request = MagicMock()
            mock_super.return_value.request = mock_request

            self.client.request("GET", self.local_host)

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})

            self.assertEqual(headers.get("PL-Calling-Class"), mock_calling_class)
            mock_get_calling_class.assert_called_once()

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
