# Level 2: Interactive Scientific Calculator

A modern, responsive, and robust interactive calculator built exclusively with vanilla HTML5, CSS3, and JavaScript (zero external libraries or frameworks).

---

## Features

- Proper Operator Precedence: Implements Dijkstra's Shunting-Yard algorithm to parse mathematical expressions and evaluate them with strict mathematical order of operations (BODMAS / PEMDAS).
  - Parentheses: `( )`
  - Unary negation: `+/-`
  - Exponentiation: `^` (right-associative)
  - Multiplication & Division: `*`, `/`, `%` (left-associative)
  - Addition & Subtraction: `+`, `-` (left-associative)
- Examples:
  - `2 + 3 * 4` evaluates to `14` (not 20).
  - `(2 + 3) * 4` evaluates to `20`.
  - `10 - 3 + 2` evaluates to `9` (not 5).
  - `2 ^ 3` evaluates to `8`.
- Full Physical Keyboard Support:
  - Number keys `0-9`
  - Operators: `+`, `-`, `*`, `/`, `^`, `%`
  - Parentheses: `(`, `)`
  - Calculation: `Enter` or `=`
  - Delete: `Backspace`
  - Clear: `Escape` or `c` / `C`
  - Real-time visual key press animation (corresponding on-screen button flashes on keypress).
- Calculation History:
  - Records previous expressions and answers.
  - Stored in browser `localStorage` for persistence across reloads.
  - Click any past calculation to restore it into the calculator.
- Safety & Precision:
  - Safe parsing without `eval()`.
  - Catches division by zero cleanly ("Cannot divide by 0").
  - Fixes binary floating point precision artifacts (e.g., `0.1 + 0.2 = 0.3`).

---

## How to Run

Since this is built with pure HTML/CSS/JS, no build step or node installation is required.

### Method 1: Open Directly in Browser
Double-click `index.html` in your file explorer or open it directly in Chrome, Edge, or Firefox.

### Method 2: Local HTTP Server (Optional)
Run Python's built-in static server:
```bash
python -m http.server 3000
```
Then navigate to `http://localhost:3000` in your web browser.
