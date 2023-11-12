import json
from httpx import Response

from starlette.exceptions import HTTPException


class ErrorRelay:
    """
    ErrorRelay forwards the error from server to client.

    e.g. When ValueError is raised in server side and is intended to be
    shown to the user (sending the request with client), ErrorRelay will
    catch the error and raise it in client side.
    """

    @staticmethod
    def encode_error_in_http_exception(error: Exception) -> HTTPException:
        """
        Encode error in HTTPException.
        """
        return HTTPException(
            status_code=400,
            headers={"ErrorRelay": json.dumps({
                "type": error.__class__.__name__,
                "message": str(error)
            })}
        )

    @staticmethod
    def try_decode_error_from_http_response(response: Response) -> Exception | None:
        """
        Try to decode error from HTTPException.
        """
        assert response.is_error

        if response.headers is None or "ErrorRelay" not in response.headers:
            return None

        error = json.loads(response.headers["ErrorRelay"])

        error_type = error["type"]
        error_message = error["message"]

        error_class = getattr(__import__("builtins"), error_type)

        return error_class(error_message)
