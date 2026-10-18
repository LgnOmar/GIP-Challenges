"""
Test Suite for Level 3: Unique Binary String Finder
"""

import pytest
from solution import find_different_binary_string, is_valid_solution


def test_example_1():
    nums = ["00", "11"]
    res = find_different_binary_string(nums)
    assert is_valid_solution(nums, res)
    assert res not in nums
    assert len(res) == 2


def test_example_2():
    nums = ["000", "101", "111"]
    res = find_different_binary_string(nums)
    assert is_valid_solution(nums, res)
    assert res not in nums
    assert len(res) == 3


def test_single_element_zero():
    nums = ["0"]
    res = find_different_binary_string(nums)
    assert res == "1"
    assert is_valid_solution(nums, res)


def test_single_element_one():
    nums = ["1"]
    res = find_different_binary_string(nums)
    assert res == "0"
    assert is_valid_solution(nums, res)


def test_two_elements_reversed():
    nums = ["01", "10"]
    res = find_different_binary_string(nums)
    assert is_valid_solution(nums, res)
    assert res not in nums


def test_four_elements():
    nums = ["0000", "0001", "0010", "0100"]
    res = find_different_binary_string(nums)
    assert is_valid_solution(nums, res)
    assert res not in nums
    assert len(res) == 4


def test_five_elements_all_ones_except_diag():
    nums = [
        "01111",
        "10111",
        "11011",
        "11101",
        "11110",
    ]
    res = find_different_binary_string(nums)
    assert is_valid_solution(nums, res)
    assert res not in nums
    assert len(res) == 5
    # Since diagonal elements are all '0', result must be "11111"
    assert res == "11111"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
