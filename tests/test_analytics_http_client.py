import unittest
from unittest.mock import patch, MagicMock
import httpx
from usage_analytics import AnalyticsHttpClient, ANALYTICS_TO_TRACK


class TestAnalyticsHttpClient(unittest.TestCase):
    def setUp(self):
        self.module_name = "test_module"
        self.client = AnalyticsHttpClient(module_name=self.module_name)
        
    def test_init(self):
        """Test that the client initializes with the correct module name."""
        self.assertEqual(self.client.module_name, self.module_name)
        self.assertIsInstance(self.client, httpx.Client)
        
    @patch('usage_analytics.analytics_http_client.super')
    def test_request_adds_headers(self, mock_super):
        """Test that request method adds analytics headers."""
        mock_request = MagicMock()
        mock_super.return_value.request = mock_request
        
        # Call request method
        self.client.request("GET", "https://example.com", headers={"Existing": "Header"})
        
        # Check that super().request was called with modified headers
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://example.com")
        
        # Verify headers were added
        headers = kwargs.get("headers", {})
        self.assertEqual(headers.get("Existing"), "Header")
        self.assertEqual(headers.get("X-Module-Name"), self.module_name)
        self.assertIn("X-Unique-Call-Id", headers)
        self.assertIn("X-Python-Version", headers)
        self.assertIn("X-Calling-Class", headers)
        
    @patch('usage_analytics.analytics_http_client.super')
    def test_stream_adds_headers(self, mock_super):
        """Test that stream method adds analytics headers."""
        mock_stream = MagicMock()
        mock_super.return_value.stream = mock_stream
        
        # Call stream method
        self.client.stream("GET", "https://example.com", headers={"Existing": "Header"})
        
        # Check that super().stream was called with modified headers
        args, kwargs = mock_stream.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://example.com")
        
        # Verify headers were added
        headers = kwargs.get("headers", {})
        self.assertEqual(headers.get("Existing"), "Header")
        
        # Verify all analytics headers from ANALYTICS_TO_TRACK were added
        for header_name, _ in ANALYTICS_TO_TRACK:
            self.assertIn(header_name, headers)
            
        # Verify specific header values
        self.assertEqual(headers.get("X-Module-Name"), self.module_name)
        self.assertIsNotNone(headers.get("X-Unique-Call-Id"))
        self.assertIsNotNone(headers.get("X-Python-Version"))
        self.assertIsNotNone(headers.get("X-Calling-Class"))


if __name__ == "__main__":
    unittest.main()
