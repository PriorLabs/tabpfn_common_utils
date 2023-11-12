import json
from functools import wraps

from fastapi import HTTPException


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
    def try_decode_error_from_http_exception(http_exception: HTTPException) -> Exception | None:
        """
        Try to decode error from HTTPException.
        """
        if http_exception.headers is None or "ErrorRelay" not in http_exception.headers:
            return None

        error = json.loads(http_exception.headers["ErrorRelay"])

        error_type = error["type"]
        error_message = error["message"]

        error_class = getattr(__import__("builtins"), error_type)

        return error_class(error_message)

    @staticmethod
    def intercept_http_exception(func: callable):
        """
        Intercept HTTPException and try decoding error from it.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException as http_exception:
                error = ErrorRelay.try_decode_error_from_http_exception(http_exception)
                if error is not None:
                    raise error
                else:
                    raise http_exception
        return wrapper

