"""Runtime environment detection for telemetry."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Literal


@dataclass
class Runtime:
    """Runtime environment."""

    interactive: bool
    kernel: Literal["ipython", "jupyter", "tty"] | None = None


def get_runtime() -> Runtime:
    """Get the runtime environment.

    Returns:
        The runtime environment.
    """
    # First check for IPython
    if _is_ipy():
        return Runtime(interactive=True, kernel="ipython")

    # Jupyter kernel
    if _is_jupyter_kernel():
        return Runtime(interactive=True, kernel="jupyter")

    # TTY
    if _is_tty():
        return Runtime(interactive=True, kernel="tty")

    # Default to non-interactive
    return Runtime(interactive=False, kernel=None)


def _is_ipy() -> bool:
    """Check if the current environment is an IPython notebook.

    Returns:
        True if the environment is an IPython notebook, False otherwise.
    """
    try:
        from IPython import get_ipython  # type: ignore[import-untyped]

        return get_ipython() is not None
    except ImportError:
        return False


def _is_jupyter_kernel() -> bool:
    """Check if the current environment is a Jupyter kernel.

    Returns:
        True if the current environment is a Jupyter kernel, False otherwise.
    """
    if "ipykernel" in sys.modules:
        return True

    # Common hints used by Jupyter frontends
    jupyter_env_vars = {
        "JPY_PARENT_PID",
        "JUPYTERHUB_API_URL",
        "JUPYTERHUB_USER",
        "COLAB_RELEASE_TAG",
    }
    return any(os.environ.get(k) for k in jupyter_env_vars)


def _is_tty() -> bool:
    """Check if the current environment is a TTY.

    Returns:
        True if the current environment is a TTY, False otherwise.
    """
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (OSError, AttributeError, IndexError):
        return False
