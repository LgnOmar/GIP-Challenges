"""
Level 3: First Missing Positive
GDG Algiers - Challenge 02: Medium

Problem:
Given an unsorted array of integers nums, return the smallest positive integer
(strictly greater than 0) that does not appear in the array.

Approach (Cyclic Placement / In-Place Index Mapping):
For an array of length n, the answer must be in the range [1, n + 1].
We place each number x (where 1 <= x <= n) at its target index (x - 1)
by swapping nums[i] with nums[nums[i] - 1].
Each swap puts at least one number in its correct final position,
yielding O(n) time complexity and O(1) auxiliary space.

After placement, the first index i where nums[i] != i + 1 identifies
the missing positive integer (i + 1). If all match, the answer is n + 1.
"""

import sys
import re
from typing import List


def first_missing_positive(nums: List[int]) -> int:
    """
    Finds the smallest positive integer missing from nums.

    Time Complexity: O(n)
    Auxiliary Space Complexity: O(1)
    """
    n = len(nums)

    for i in range(n):
        # Place nums[i] into its ideal index (nums[i] - 1) if in range [1, n]
        # and not already at that position (handles duplicates)
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target_idx = nums[i] - 1
            nums[i], nums[target_idx] = nums[target_idx], nums[i]

    # Find first index where nums[i] != i + 1
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1

    return n + 1


def parse_integers(text: str) -> List[int]:
    """Parses a string of integers separated by spaces, commas, or brackets."""
    # Strip brackets if user inputs list-like format like "[1, 2, 0]"
    cleaned = text.strip().lstrip("[").rstrip("]")
    if not cleaned:
        return []
    # Split by comma or whitespace
    tokens = [t for t in re.split(r"[\s,]+", cleaned) if t]
    return [int(t) for t in tokens]


def run_interactive():
    print("=== First Missing Positive - Interactive CLI ===")
    print("Enter integers separated by space or comma (e.g. '3, 4, -1, 1' or '[0, -2, 1, 2]').")
    print("Type 'q' or 'exit' to quit.\n")

    while True:
        try:
            line = input("Enter nums > ").strip()
            if not line:
                continue
            if line.lower() in ("q", "quit", "exit"):
                print("Exiting.")
                break

            nums = parse_integers(line)
            # Use a copy so original array can be displayed
            result = first_missing_positive(list(nums))
            print(f"Input : {nums}")
            print(f"First Missing Positive: {result}\n")
        except ValueError:
            print("Error: Please enter valid integers separated by space or commas.\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    # If arguments are passed via command line, e.g. python solution.py 3 4 -1 1
    if len(sys.argv) > 1:
        raw_args = " ".join(sys.argv[1:])
        try:
            nums = parse_integers(raw_args)
            result = first_missing_positive(list(nums))
            print(f"Input : {nums}")
            print(f"First Missing Positive: {result}")
        except ValueError:
            print("Error: Command line arguments must be integers.")
            sys.exit(1)
    else:
        run_interactive()
