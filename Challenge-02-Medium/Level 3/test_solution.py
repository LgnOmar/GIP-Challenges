import pytest
from solution import first_missing_positive


@pytest.mark.parametrize(
    "nums, expected",
    [
        # Examples from specification
        ([0, -2, 1, 2], 3),
        ([1, 2, 3], 4),
        ([-3, -1, 0], 1),
        ([2, 2, 1], 3),
        ([], 1),
        ([3, 4, -1, 1], 2),
        # Single element cases
        ([1], 2),
        ([2], 1),
        ([0], 1),
        ([-5], 1),
        # Array with gaps
        ([7, 8, 9, 11, 12], 1),
        ([1, 1000], 2),
        ([1, 2, 0], 3),
        # Duplicate values
        ([1, 1, 1, 1], 2),
        ([2, 2, 2, 2], 1),
        ([3, 3, 1, 4, 1], 2),
        # Consecutive positive sequence
        ([1, 2, 3, 4, 5], 6),
        # Mixed negative, zeros, large numbers, and duplicates
        ([-10, -3, 0, 5, 1, 2, 100, 3, -1], 4),
        ([100, 200, 300], 1),
        ([1, 2, 3, 5], 4),
    ],
)
def test_first_missing_positive(nums, expected):
    # Pass a copy to avoid mutating parametrized input across test runs
    assert first_missing_positive(list(nums)) == expected
