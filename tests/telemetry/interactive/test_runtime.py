from __future__ import annotations

import os
import pytest
import sys
from unittest.mock import patch

from tabpfn_common_utils.telemetry.interactive.runtime import (
    _is_ipy,
    _is_jupyter_kernel,
    _is_tty,
    get_runtime,
)


class TestRuntimeDetection:
    """Test runtime environment detection."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.module = "tabpfn_common_utils.telemetry.interactive.runtime"

    def test_get_runtime_interactive_ipython(self) -> None:
        """Test that IPython environments are detected as interactive."""

        with patch(f"{self.module}._is_ipy", return_value=True):
            assert get_runtime().interactive is True

    def test_get_runtime_interactive_jupyter(self) -> None:
        """Test that Jupyter environments are detected as interactive."""
        with (
            patch(f"{self.module}._is_ipy", return_value=False),
            patch(f"{self.module}._is_jupyter_kernel", return_value=True),
        ):
            assert get_runtime().interactive is True

    def test_get_runtime_default_noninteractive(self) -> None:
        """Test that default environment is noninteractive."""
        with (
            patch(f"{self.module}._is_ipy", return_value=False),
            patch(f"{self.module}._is_jupyter_kernel", return_value=False),
        ):
            assert get_runtime().interactive is False


class TestIPythonCheck:
    """Test IPython environment detection."""

    def test_is_ipy_returns_bool(self) -> None:
        """Test that _is_ipy always returns a boolean."""
        result = _is_ipy()
        assert isinstance(result, bool)

    def test_is_ipy_handles_import_error(self) -> None:
        """Test that _is_ipy handles import errors gracefully."""
        # Since IPython is not installed, this should return False
        result = _is_ipy()
        assert result is False


class TestJupyterKernelCheck:
    """Test Jupyter kernel detection."""

    def test_is_jupyter_kernel_with_ipykernel(self) -> None:
        """Test Jupyter detection with ipykernel in sys.modules."""
        with patch.dict(sys.modules, {"ipykernel": object()}):
            assert _is_jupyter_kernel() is True

    def test_is_jupyter_kernel_with_jupyter_env_vars(self) -> None:
        """Test Jupyter detection with Jupyter environment variables."""
        with patch.dict(os.environ, {"JPY_PARENT_PID": "12345"}):
            assert _is_jupyter_kernel() is True

    def test_is_jupyter_kernel_with_colab(self) -> None:
        """Test Jupyter detection with Colab environment."""
        with patch.dict(os.environ, {"COLAB_RELEASE_TAG": "r20231201"}):
            assert _is_jupyter_kernel() is True

    def test_is_jupyter_kernel_no_indicators(self) -> None:
        """Test Jupyter detection with no indicators."""
        with (
            patch.dict(sys.modules, {}, clear=True),
            patch.dict(os.environ, {}, clear=True),
        ):
            assert _is_jupyter_kernel() is False


class TestTTYCheck:
    """Test TTY detection."""

    def test_is_tty_with_tty(self) -> None:
        """Test TTY detection when stdin/stdout are TTY."""
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            assert _is_tty() is True

    def test_is_tty_without_tty(self) -> None:
        """Test TTY detection when stdin/stdout are not TTY."""
        with (
            patch("sys.stdin.isatty", return_value=False),
            patch("sys.stdout.isatty", return_value=False),
        ):
            assert _is_tty() is False

    def test_is_tty_mixed_tty(self) -> None:
        """Test TTY detection with mixed TTY status."""
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=False),
        ):
            assert _is_tty() is False

    def test_is_tty_exception(self) -> None:
        """Test TTY detection with exception."""
        with patch("sys.stdin.isatty", side_effect=OSError):
            assert _is_tty() is False
