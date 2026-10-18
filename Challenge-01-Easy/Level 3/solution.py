"""
Level 3: Unique Binary String Finder (Cantor's Diagonalization)
GDG Algiers - Challenge 01: Easy

Problem:
Given an array `nums` containing `n` unique binary strings, each of length `n`,
return any binary string of length `n` that does not appear in `nums`.

Approach (Cantor's Diagonal Argument):
Instead of generating all 2^n possible binary strings or doing set lookups,
we can build an answer directly in O(n) time and O(1) extra space.
For each index i from 0 to n-1:
- If nums[i][i] is '0', set result[i] = '1'
- If nums[i][i] is '1', set result[i] = '0'

Why this is guaranteed to work:
The constructed string differs from nums[0] at index 0.
It differs from nums[1] at index 1.
...
It differs from nums[i] at index i.
Therefore, the result cannot match any string currently in nums.
"""

import sys
from typing import List


def find_different_binary_string(nums: List[str]) -> str:
    """
    Finds a binary string of length n not present in nums.

    Time Complexity: O(n)
    Space Complexity: O(n) for the output string
    """
    n = len(nums)
    return "".join("1" if nums[i][i] == "0" else "0" for i in range(n))


def is_valid_solution(nums: List[str], candidate: str) -> bool:
    """Helper to verify candidate string satisfies all constraints."""
    n = len(nums)
    if len(candidate) != n:
        return False
    if not all(c in ("0", "1") for c in candidate):
        return False
    if candidate in nums:
        return False
    return True


if __name__ == "__main__":
    # If arguments are passed via terminal: e.g. python solution.py 000 101 111
    if len(sys.argv) > 1:
        user_inputs = sys.argv[1:]
        result = find_different_binary_string(user_inputs)
        valid = is_valid_solution(user_inputs, result)
        print(f"Input : {user_inputs}")
        print(f"Result: {result} (Valid: {valid})")
        sys.exit(0)

    # Default: Run built-in demonstrations
    print("=== Built-in Demonstrations ===")
    demo_cases = [
        ["00", "11"],
        ["000", "101", "111"],
        ["01", "10"],
        ["0"],
        ["1"],
        ["111", "011", "001"],
    ]

    for tc in demo_cases:
        res = find_different_binary_string(tc)
        valid = is_valid_solution(tc, res)
        print(f"Input: {tc} -> Result: '{res}' (Valid: {valid})")

    # Interactive input prompt
    print("\n=== Interactive Test Mode ===")
    print("Enter binary strings separated by space (or press Enter to quit):")
    try:
        user_line = input("> ").strip()
        if user_line:
            items = user_line.split()
            n = len(items)
            # Verify basic format
            if all(len(s) == n and all(c in "01" for c in s) for s in items):
                res = find_different_binary_string(items)
                valid = is_valid_solution(items, res)
                print(f"Result : '{res}'")
                print(f"Valid  : {valid} (Length matches {n} and does not appear in input)")
            else:
                print(f"Note: You entered {n} items. Each item must be a binary string of length {n}.")
    except (EOFError, KeyboardInterrupt):
        pass
