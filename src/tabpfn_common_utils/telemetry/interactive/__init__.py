"""Interactive telemetry containing prompts and runtime detection."""

from __future__ import annotations


try:
    # Import the specific functions to expose
    from .flows import ping, subscribe
    from .runtime import get_runtime

    __all__ = ["ping", "subscribe", "get_runtime"]

except ImportError:

    def __getattr__(name):
        e = ImportError(
            "Interactive telemetry is not available. "
            "Install with: pip install tabpfn_common_utils[interactive]"
        )
        raise e

    __all__ = []
