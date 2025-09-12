"""Tests for telemetry decorators."""

from __future__ import annotations


from tabpfn_common_utils.telemetry.core.decorators import _round_dims


class TestRoundDims:
    """Test the round_dims function."""

    def test_round_dims_examples(self) -> None:
        """Test the specific examples provided."""
        # Test the examples from the user's request
        assert _round_dims((7, 10)) == (10, 10)
        assert _round_dims((156, 60)) == (200, 75)  # 156 -> 200, 60 -> 75
        assert _round_dims((953, 17)) == (1000, 20)  # 953 -> 1000, 17 -> 20

    def test_round_dims_empty_shape(self) -> None:
        """Test handling of empty shape."""
        assert _round_dims((0, 0)) == (10, 5)  # Empty shape rounds to minimum values

    def test_round_dims_row_limits(self) -> None:
        """Test rounding for different row limits."""
        # Test each row limit: [10, 50, 75, 100, 150, 200, 500, 1000]
        assert _round_dims((5, 10)) == (10, 10)  # 5 -> 10
        assert _round_dims((25, 10)) == (50, 10)  # 25 -> 50
        assert _round_dims((60, 10)) == (75, 10)  # 60 -> 75
        assert _round_dims((85, 10)) == (100, 10)  # 85 -> 100
        assert _round_dims((120, 10)) == (150, 10)  # 120 -> 150
        assert _round_dims((175, 10)) == (200, 10)  # 175 -> 200
        assert _round_dims((300, 10)) == (500, 10)  # 300 -> 500
        assert _round_dims((750, 10)) == (1000, 10)  # 750 -> 1000

    def test_round_dims_col_limits(self) -> None:
        """Test rounding for different column limits."""
        # Test each column limit: [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
        assert _round_dims((100, 3)) == (100, 5)  # 3 -> 5
        assert _round_dims((100, 8)) == (100, 10)  # 8 -> 10
        assert _round_dims((100, 12)) == (100, 15)  # 12 -> 15
        assert _round_dims((100, 18)) == (100, 20)  # 18 -> 20
        assert _round_dims((100, 23)) == (100, 25)  # 23 -> 25
        assert _round_dims((100, 28)) == (100, 30)  # 28 -> 30
        assert _round_dims((100, 35)) == (100, 40)  # 35 -> 40
        assert _round_dims((100, 45)) == (100, 50)  # 45 -> 50
        assert _round_dims((100, 65)) == (100, 75)  # 65 -> 75
        assert _round_dims((100, 85)) == (100, 100)  # 85 -> 100

    def test_round_dims_large_numbers(self) -> None:
        """Test rounding for numbers larger than defined limits."""
        # Large rows should round to nearest 50
        assert _round_dims((1200, 10)) == (1200, 10)  # 1200 -> 1200 (nearest 50)
        assert _round_dims((1250, 10)) == (1250, 10)  # 1250 -> 1250 (nearest 50)
        assert _round_dims((1275, 10)) == (1250, 10)  # 1275 -> 1250 (nearest 50)

        # Large columns should round to nearest 50
        assert _round_dims((100, 120)) == (100, 100)  # 120 -> 100 (nearest 50)
        assert _round_dims((100, 150)) == (100, 150)  # 150 -> 150 (nearest 50)
        assert _round_dims((100, 175)) == (100, 150)  # 175 -> 150 (nearest 50)

    def test_round_dims_edge_cases(self) -> None:
        """Test edge cases around the limits."""
        # Test exact limits for rows: [10, 50, 75, 100, 150, 200, 500, 1000]
        assert _round_dims((10, 10)) == (10, 10)
        assert _round_dims((50, 20)) == (50, 20)
        assert _round_dims((75, 30)) == (75, 30)
        assert _round_dims((100, 40)) == (100, 40)
        assert _round_dims((150, 50)) == (150, 50)
        assert _round_dims((200, 75)) == (200, 75)
        assert _round_dims((500, 100)) == (500, 100)
        assert _round_dims((1000, 100)) == (1000, 100)

        # Test exact limits for columns: [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
        assert _round_dims((100, 5)) == (100, 5)
        assert _round_dims((100, 10)) == (100, 10)
        assert _round_dims((100, 15)) == (100, 15)
        assert _round_dims((100, 20)) == (100, 20)
        assert _round_dims((100, 25)) == (100, 25)
        assert _round_dims((100, 30)) == (100, 30)
        assert _round_dims((100, 40)) == (100, 40)
        assert _round_dims((100, 50)) == (100, 50)
        assert _round_dims((100, 75)) == (100, 75)
        assert _round_dims((100, 100)) == (100, 100)

        # Test just above limits
        assert _round_dims((11, 6)) == (50, 10)  # 11 -> 50, 6 -> 10
        assert _round_dims((51, 11)) == (75, 15)  # 51 -> 75, 11 -> 15
        assert _round_dims((76, 21)) == (100, 25)  # 76 -> 100, 21 -> 25

    def test_round_dims_single_digit(self) -> None:
        """Test very small dimensions."""
        assert _round_dims((1, 1)) == (10, 5)
        assert _round_dims((3, 7)) == (10, 10)
        assert _round_dims((9, 9)) == (10, 10)

    def test_round_dims_new_column_ranges(self) -> None:
        """Test the new column limit ranges."""
        # Test ranges between new limits: [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
        assert _round_dims((100, 6)) == (100, 10)  # 6 -> 10
        assert _round_dims((100, 9)) == (100, 10)  # 9 -> 10
        assert _round_dims((100, 11)) == (100, 15)  # 11 -> 15
        assert _round_dims((100, 14)) == (100, 15)  # 14 -> 15
        assert _round_dims((100, 16)) == (100, 20)  # 16 -> 20
        assert _round_dims((100, 19)) == (100, 20)  # 19 -> 20
        assert _round_dims((100, 21)) == (100, 25)  # 21 -> 25
        assert _round_dims((100, 24)) == (100, 25)  # 24 -> 25
        assert _round_dims((100, 26)) == (100, 30)  # 26 -> 30
        assert _round_dims((100, 29)) == (100, 30)  # 29 -> 30
        assert _round_dims((100, 31)) == (100, 40)  # 31 -> 40
        assert _round_dims((100, 39)) == (100, 40)  # 39 -> 40
        assert _round_dims((100, 41)) == (100, 50)  # 41 -> 50
        assert _round_dims((100, 49)) == (100, 50)  # 49 -> 50
        assert _round_dims((100, 51)) == (100, 75)  # 51 -> 75
        assert _round_dims((100, 74)) == (100, 75)  # 74 -> 75
        assert _round_dims((100, 76)) == (100, 100)  # 76 -> 100
        assert _round_dims((100, 99)) == (100, 100)  # 99 -> 100

    def test_round_dims_anonymization_purpose(self) -> None:
        """Test that the function serves its anonymization purpose."""
        # Test that similar shapes get rounded to the same values
        assert _round_dims((7, 10)) == _round_dims((9, 10)) == (10, 10)
        assert _round_dims((95, 45)) == _round_dims((99, 49)) == (100, 50)

        # Test with new column limits - same range should round to same value
        assert _round_dims((100, 11)) == _round_dims((100, 14)) == (100, 15)
        assert _round_dims((100, 16)) == _round_dims((100, 19)) == (100, 20)
        assert _round_dims((100, 21)) == _round_dims((100, 24)) == (100, 25)
        assert _round_dims((100, 51)) == _round_dims((100, 74)) == (100, 75)

        # Test with new row limits - same range should round to same value
        assert _round_dims((11, 10)) == _round_dims((49, 10)) == (50, 10)
        assert _round_dims((51, 10)) == _round_dims((74, 10)) == (75, 10)
        assert _round_dims((76, 10)) == _round_dims((99, 10)) == (100, 10)

    def test_round_dims_return_type(self) -> None:
        """Test that the function returns the correct type."""
        result = _round_dims((100, 50))
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)

    def test_round_dims_special_cases(self) -> None:
        """Test special cases that might occur in practice."""
        # Test the exact examples from user request with new column limits
        assert _round_dims((156, 60)) == (200, 75)  # 156 -> 200, 60 -> 75
        assert _round_dims((953, 17)) == (1000, 20)  # 953 -> 1000, 17 -> 20

        # Test some intermediate values
        assert _round_dims((1234, 67)) == (1200, 75)  # 1234 -> 1200, 67 -> 75
        assert _round_dims((876, 89)) == (1000, 100)  # 876 -> 1000, 89 -> 100
