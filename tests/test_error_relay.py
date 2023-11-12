import unittest
from httpx import Response

from starlette.exceptions import HTTPException

from tabpfn_common_utils.error_relay import ErrorRelay


class TestErrorRelay(unittest.TestCase):

    @staticmethod
    def _get_http_exception_response(encode_error: Exception = None) -> Response:
        if encode_error is not None:
            exception = ErrorRelay.encode_error_in_http_exception(encode_error)
        else:
            exception = HTTPException(status_code=400)

        response = Response(
            status_code=400,
            headers=exception.headers if exception.headers is not None else None,
        )
        return response

    def test_encode_error_in_http_exception(self):
        error = ValueError("test error")
        http_exception = ErrorRelay.encode_error_in_http_exception(error)
        self.assertEqual(http_exception.status_code, 400)
        self.assertEqual(http_exception.headers["ErrorRelay"], '{"type": "ValueError", "message": "test error"}')

    def test_try_decode_error_from_http_exception(self):
        error = ValueError("test error")
        response = self._get_http_exception_response(encode_error=error)
        decoded_error = ErrorRelay.try_decode_error_from_http_response(response)
        self.assertEqual(type(decoded_error), ValueError)
        self.assertEqual(str(decoded_error), "test error")
