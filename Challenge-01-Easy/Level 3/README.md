# Level 3: Unique Binary String Finder

Solution for **Level 3** of **Challenge 01: Easy** (GDG Algiers Dev Department).

---

## Problem Description

Given an array `nums` containing `n` unique binary strings, each of length `n`, return any binary string of length `n` that does not appear in `nums`.

### Constraints
- A binary string contains only `'0'` and `'1'`.
- The number of strings `n` equals the length of each string (`len(nums) == len(nums[i]) == n`).
- `nums` contains unique strings.

### Examples
- **Example 1**:
  - Input: `nums = ["00", "11"]`
  - Output: `"10"` (or `"01"`)
- **Example 2**:
  - Input: `nums = ["000", "101", "111"]`
  - Output: `"110"` (or `"001"`, `"010"`, etc.)

---

## Mathematical Approach: Cantor's Diagonalization

Instead of generating all 2^n binary combinations or using hash sets, we use **Cantor's Diagonal Argument**:

We construct an answer string S of length n by inverting the diagonal elements of the given matrix of strings:

```text
For i from 0 to n-1:
  S[i] = '1' if nums[i][i] == '0' else '0'
```

### Why this is mathematically guaranteed to work:
1. S differs from nums[0] at index 0.
2. S differs from nums[1] at index 1.
3. ...
4. S differs from nums[i] at index i.

Because S differs from every string nums[i] by at least one character, S cannot be equal to any string in nums.

---

## Complexity Analysis

- Time Complexity: O(n) -- We examine exactly one character from each string (nums[i][i]).
- Space Complexity: O(n) -- Auxiliary space required only to construct the output string.

---

## How to Use and Test the Solution

You can test and experiment with the solution using any of the following 4 methods:

### Method 1: Pass Binary Strings Directly via Terminal

Pass your strings separated by spaces as command-line arguments:

```bash
# Example with 2 binary strings of length 2
python solution.py 00 11
```
Output:
```text
Input : ['00', '11']
Result: 10 (Valid: True)
```

```bash
# Example with 3 binary strings of length 3
python solution.py 000 101 111
```
Output:
```text
Input : ['000', '101', '111']
Result: 110 (Valid: True)
```

```bash
# Example with 4 binary strings of length 4
python solution.py 0000 0001 0010 0100
```
Output:
```text
Input : ['0000', '0001', '0010', '0100']
Result: 1101 (Valid: True)
```

---

### Method 2: Interactive Test Prompt

Run `solution.py` without arguments:

```bash
python solution.py
```

It will execute the built-in demonstrations and then prompt you for custom input:
```text
=== Built-in Demonstrations ===
Input: ['00', '11'] -> Result: '10' (Valid: True)
Input: ['000', '101', '111'] -> Result: '110' (Valid: True)
Input: ['01', '10'] -> Result: '11' (Valid: True)
Input: ['0'] -> Result: '1' (Valid: True)
Input: ['1'] -> Result: '0' (Valid: True)
Input: ['111', '011', '001'] -> Result: '000' (Valid: True)

=== Interactive Test Mode ===
Enter binary strings separated by space (or press Enter to quit):
> 000 101 111
Result : '110'
Valid  : True (Length matches 3 and does not appear in input)
```

---

### Method 3: Run the Automated Test Suite

Run pytest to verify all 7 test cases (testing single strings, edge cases, and larger matrices):

```bash
pytest test_solution.py -v
```

Output:
```text
test_solution.py::test_example_1 PASSED
test_solution.py::test_example_2 PASSED
test_solution.py::test_single_element_zero PASSED
test_solution.py::test_single_element_one PASSED
test_solution.py::test_two_elements_reversed PASSED
test_solution.py::test_four_elements PASSED
test_solution.py::test_five_elements_all_ones_except_diag PASSED
```

---

### Method 4: Test in Python Interactive REPL

Launch Python in interactive mode:

```bash
python -i solution.py
```

Call the function directly with any list of strings:
```python
>>> find_different_binary_string(["01", "10"])
'11'

>>> find_different_binary_string(["000", "010", "100"])
'101'
```
