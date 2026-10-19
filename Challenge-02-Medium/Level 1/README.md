# Challenge 02: Medium - Level 1

## Country Search with Autocomplete

A performant client-side search box with autocomplete, built entirely in vanilla HTML, CSS, and JavaScript. No frameworks or external dependencies.

---

### Features

- **Mid-word matching**: Typing `land` returns Iceland, Ireland, New Zealand, Poland, etc.
- **Accent-insensitive**: `cote` matches `Cote d'Ivoire`. `sao` matches `Sao Tome and Principe`. `cote`, `cote`, and `coté` are all treated equivalently.
- **Apostrophe-normalized**: Curly quotes and straight apostrophes are treated as equivalent, so `cote d'ivoire` matches `Cote d'Ivoire` regardless of apostrophe style.
- **Relevance-ranked results**:
  1. Entries where the name starts with the query (highest priority)
  2. Entries where a word within the name starts with the query
  3. Entries containing the query as a mid-word substring
- **Keyboard navigation**: Arrow keys to navigate, Enter to select, Escape to dismiss.
- **Maximum 10 suggestions** displayed at once.
- **Responsive and accessible**: Works on all screen sizes, uses ARIA attributes for screen readers.

---

### Technical Approach

**Normalization**: Uses Unicode NFD decomposition to strip combining diacritical marks (accents), making characters like `o` and `o` equivalent for search purposes. All apostrophe variants (curly, prime, etc.) are normalized to a standard straight apostrophe.

**Algorithm**: The search iterates through the pre-normalized dataset and classifies each match into one of three relevance tiers based on where the match occurs, then concatenates the tiers in priority order and returns the top 10.

**Performance**: Normalized forms are pre-computed at load time to avoid repeated normalization during search.

---

### How to Use

1. Open `index.html` in any modern browser (or use a local server since `data.js` uses ES module exports):
   ```bash
   # If you have Python installed:
   python -m http.server 8080

   # Or if you have Node.js installed:
   npx -y serve .
   ```
2. Navigate to `http://localhost:8080` in your browser.
3. Type in the search box and see autocomplete suggestions appear.
4. Use arrow keys to navigate suggestions, Enter to select, Escape to dismiss.

---

### File Structure

```
Level 1/
  data.js      -- Country dataset (110 entries with accented names)
  index.html   -- HTML structure and semantic markup
  style.css    -- Dark-mode glassmorphism styling
  search.js    -- Autocomplete algorithm and UI logic
  README.md    -- This file
```
