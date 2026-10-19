# Challenge 02: Medium - Level 3

## First Missing Positive

Finds the smallest positive integer (strictly greater than 0) that does not appear in an unsorted array of integers.

---

### Approach: Cyclic Placement (In-Place Index Mapping)

For an array `nums` of length `n`, the smallest missing positive integer must fall within the range `[1, n + 1]`.
- If all numbers from `1` to `n` are present, the answer is `n + 1`.
- Otherwise, at least one integer between `1` and `n` is absent, so the answer is in `[1, n]`.

#### Algorithm
1. **Rearrange in-place**: Iterate through `nums`. For each index `i`, as long as `1 <= nums[i] <= n` and `nums[nums[i] - 1] != nums[i]`, swap `nums[i]` with the element at its target index `nums[i] - 1`.
   - The condition `nums[nums[i] - 1] != nums[i]` naturally prevents infinite loops when duplicate numbers are present.
2. **Scan for first mismatch**: Iterate from `0` to `n - 1`. The first index `i` where `nums[i] != i + 1` indicates that `i + 1` is the smallest missing positive.
3. **Fallback**: If all positions match (`nums[i] == i + 1` for all `i`), return `n + 1`.

---

### Complexity Analysis

- **Time Complexity: O(n)**: Although there is a nested `while` loop, each swap places at least one number into its correct position `x - 1`. Because an element is swapped into its correct position at most once, at most `n` swaps occur across the entire traversal, resulting in linear `O(n)` total steps.
- **Auxiliary Space Complexity: O(1)**: The reordering is done entirely in-place within the input array without allocating extra collections or hash sets.

---

### How to Use

#### 1. Interactive Mode
Run without arguments to start the interactive prompt:
```bash
python solution.py
```
Example session:
```text
=== First Missing Positive - Interactive CLI ===
Enter integers separated by space or comma (e.g. '3, 4, -1, 1' or '[0, -2, 1, 2]').
Type 'q' or 'exit' to quit.

Enter nums > 3, 4, -1, 1
Input : [3, 4, -1, 1]
First Missing Positive: 2

Enter nums > [0, -2, 1, 2]
Input : [0, -2, 1, 2]
First Missing Positive: 3

Enter nums > q
Exiting.
```

#### 2. Command-Line Arguments Mode
Pass any list of integers directly as arguments:
```bash
python solution.py 3 4 -1 1
# or
python solution.py "[0, -2, 1, 2]"
```

#### 3. Automated Tests
Run the test suite using pytest:
```bash
pytest test_solution.py
```

---

### Test Coverage

The test suite covers:
- Empty input `[]`
- Arrays containing negative integers and zeros (`[-3, -1, 0]`, `[0, -2, 1, 2]`)
- Arrays with duplicates (`[2, 2, 1]`, `[1, 1, 1, 1]`)
- Complete sequences (`[1, 2, 3]` -> `4`)
- Single element arrays (`[1]`, `[2]`, `[0]`, `[-5]`)
- Unsorted arrays with gaps (`[3, 4, -1, 1]`, `[7, 8, 9, 11, 12]`, `[1, 1000]`)
