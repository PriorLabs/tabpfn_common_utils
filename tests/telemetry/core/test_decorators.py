"""Tests for telemetry decorators."""

import pytest

from tabpfn_common_utils.telemetry.core.decorators import (
    set_extension,
    get_current_extension,
    _extension_context,
)


class TestSetExtensionDecorator:
    def test_sets_extension_context_when_none_exists(self):
        """Test that decorator sets extension context when none is active."""

        @set_extension("test_extension")
        def test_function():
            return get_current_extension()

        result = test_function()
        assert result == "test_extension"

    def test_preserves_existing_context_in_nested_calls(self):
        """Test that existing context is preserved in nested decorated functions."""

        @set_extension("outer_extension")
        def outer_function():
            @set_extension("inner_extension")
            def inner_function():
                return get_current_extension()

            return inner_function()

        result = outer_function()
        # Should preserve outer context
        assert result == "outer_extension"

    def test_extension_context_cleanup_after_execution(self):
        """Test that extension context is cleaned up after execution."""

        @set_extension("temp_extension")
        def test_function():
            return get_current_extension()

        # Before call
        assert get_current_extension() is None

        # During call
        result = test_function()
        assert result == "temp_extension"

        # After call - should be cleaned up
        assert get_current_extension() is None

    def test_multiple_nested_decorators_preserve_top_level_context(self):
        """Test that multiple levels of nesting preserve the top-level context."""

        @set_extension("level1")
        def level1():
            @set_extension("level2")
            def level2():
                @set_extension("level3")
                def level3():
                    return get_current_extension()

                return level3()

            return level2()

        result = level1()
        # Should preserve the top-level context
        assert result == "level1"

    def test_extension_context_with_exceptions(self):
        """Test that extension context is properly cleaned up even when exceptions occur."""

        @set_extension("error_extension")
        def error_function():
            raise ValueError("Test error")

        # Before call
        assert get_current_extension() is None

        # Call should raise exception but clean up context
        with pytest.raises(ValueError, match="Test error"):
            error_function()

        # After exception - context should be cleaned up
        assert get_current_extension() is None


class TestExtensionContextManager:
    def test_context_manager_sets_and_resets_extension(self):
        """Test that context manager properly sets and resets extension."""
        with _extension_context("test_extension"):
            assert get_current_extension() == "test_extension"

        # After context exit
        assert get_current_extension() is None

    def test_context_manager_with_exception(self):
        """Test that context manager cleans up even when exceptions occur."""
        with pytest.raises(ValueError):
            with _extension_context("error_extension"):
                assert get_current_extension() == "error_extension"
                raise ValueError("Test error")

        # After exception - context should be cleaned up
        assert get_current_extension() is None

    def test_nested_context_managers(self):
        """Test nested context managers preserve outer context."""
        with _extension_context("outer"):
            assert get_current_extension() == "outer"

            with _extension_context("inner"):
                assert get_current_extension() == "inner"

            # After inner context exits, should return to outer
            assert get_current_extension() == "outer"

        # After outer context exits
        assert get_current_extension() is None
