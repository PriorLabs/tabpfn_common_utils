import unittest

from tabpfn_common_utils.error_relay import ErrorRelay


class TestErrorRelay(unittest.TestCase):
    def test_encode_error_in_http_exception(self):
        error = ValueError("test error")
        http_exception = ErrorRelay.encode_error_in_http_exception(error)
        self.assertEqual(http_exception.status_code, 400)
        self.assertEqual(http_exception.headers["ErrorRelay"], '{"type": "ValueError", "message": "test error"}')

    def test_try_decode_error_from_http_exception(self):
        error = ValueError("test error")
        http_exception = ErrorRelay.encode_error_in_http_exception(error)
        decoded_error = ErrorRelay.try_decode_error_from_http_exception(http_exception)
        self.assertEqual(type(decoded_error), ValueError)
        self.assertEqual(str(decoded_error), "test error")
