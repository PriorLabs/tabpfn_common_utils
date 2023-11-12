import unittest

from fastapi import HTTPException

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

    def test_intercept_http_exception_on_http_exception_containing_value_error(self):
        def raise_http_exception_containing_value_error():
            raise ErrorRelay.encode_error_in_http_exception(ValueError())

        @ErrorRelay.intercept_http_exception
        def calling_func():
            raise_http_exception_containing_value_error()

        self.assertRaises(ValueError, calling_func)

    def test_intercept_http_exception_on_http_exception_not_containing_error(self):
        def raise_http_exception_not_containing_error():
            raise HTTPException(status_code=400)

        @ErrorRelay.intercept_http_exception
        def calling_func():
            raise_http_exception_not_containing_error()

        self.assertRaises(HTTPException, calling_func)
