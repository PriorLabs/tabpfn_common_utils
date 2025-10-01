from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

from tabpfn_common_utils.telemetry.core.service import ProductTelemetry


class TestRunsInTest:
    """Test the _runs_in_test method for detecting test environments."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test fixtures and clear cache before each test."""
        self.original_class = ProductTelemetry()  # type: ignore
        self.original_class._runs_in_test.cache_clear()

    def test_detects_pytest_current_test_env_var(self) -> None:
        """Test detection via PYTEST_CURRENT_TEST environment variable."""
        with patch.dict(
            os.environ, {"PYTEST_CURRENT_TEST": "tests/test_service.py::test_method"}
        ):
            assert self.original_class._runs_in_test() is True

    def test_detects_pytest_xdist_worker_env_var(self) -> None:
        """Test detection via PYTEST_XDIST_WORKER environment variable."""
        with patch.dict(os.environ, {"PYTEST_XDIST_WORKER": "gw0"}):
            assert self.original_class._runs_in_test() is True

    def test_detects_pytest_in_sys_modules(self) -> None:
        """Test detection via pytest in sys.modules."""
        # pytest should already be in sys.modules when running tests
        assert "pytest" in sys.modules
        assert self.original_class._runs_in_test() is True

    def test_detects_unittest_in_sys_modules(self) -> None:
        """Test detection via unittest in sys.modules."""
        with patch.dict(sys.modules, {"unittest": object()}):
            assert self.original_class._runs_in_test() is True

    def test_detects_nose_in_sys_modules(self) -> None:
        """Test detection via nose in sys.modules."""
        with patch.dict(sys.modules, {"nose": object()}):
            assert self.original_class._runs_in_test() is True

    def test_detects_pytest_in_argv(self) -> None:
        """Test detection via pytest in sys.argv[0]."""
        with patch.object(sys, "argv", ["/usr/bin/pytest", "tests/"]):
            assert self.original_class._runs_in_test() is True

    def test_detects_py_test_in_argv(self) -> None:
        """Test detection via py.test in sys.argv[0]."""
        with patch.object(sys, "argv", ["/usr/local/bin/py.test", "tests/"]):
            assert self.original_class._runs_in_test() is True

    def test_detects_pytest_uppercase_in_argv(self) -> None:
        """Test detection is case-insensitive for sys.argv[0]."""
        with patch.object(sys, "argv", ["/path/to/PYTEST", "tests/"]):
            assert self.original_class._runs_in_test() is True

    def test_caching_behavior(self) -> None:
        """Test that the function caches its result."""
        # First call should compute the result
        result1 = self.original_class._runs_in_test()

        # Check cache info
        cache_info = self.original_class._runs_in_test.cache_info()  # type: ignore
        assert cache_info.hits == 0
        assert cache_info.misses == 1

        # Second call should use cache
        result2 = self.original_class._runs_in_test()
        assert result1 == result2

        # Check cache was used
        cache_info = self.original_class._runs_in_test.cache_info()  # type: ignore
        assert cache_info.hits == 1
        assert cache_info.misses == 1

    def test_returns_bool(self) -> None:
        """Test that the function always returns a boolean."""
        result = self.original_class._runs_in_test()
        assert isinstance(result, bool)
