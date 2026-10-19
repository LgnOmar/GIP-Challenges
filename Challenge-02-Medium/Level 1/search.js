import { countries } from "./data.js";

// --- Normalization Utilities ---

/**
 * Normalize a string for accent-insensitive and apostrophe-normalized comparison.
 * Uses Unicode NFD decomposition to strip combining diacritical marks,
 * and converts all apostrophe variants to a standard straight apostrophe.
 */
function normalize(str) {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")         // strip combining diacritics
    .replace(/[\u2018\u2019\u201A\u201B]/g, "'") // curly single quotes -> straight
    .replace(/[\u2032\u2035]/g, "'")          // prime marks -> straight
    .toLowerCase();
}


// --- Pre-compute normalized names once at load time ---

const dataset = countries.map((country) => ({
  ...country,
  normalized: normalize(country.name),
}));


// --- Search Algorithm ---

const MAX_SUGGESTIONS = 10;

/**
 * Search the dataset for entries matching the query.
 * Returns up to MAX_SUGGESTIONS results, ranked by relevance:
 *   1. Name starts with query
 *   2. Any word in the name starts with query
 *   3. Mid-word / substring match
 * Within each tier, results keep their original dataset order.
 */
function search(query) {
  const normalizedQuery = normalize(query.trim());

  if (!normalizedQuery) return [];

  const startsWith = [];
  const wordStartsWith = [];
  const contains = [];

  for (const entry of dataset) {
    const idx = entry.normalized.indexOf(normalizedQuery);
    if (idx === -1) continue;

    if (idx === 0) {
      // Name starts with query
      startsWith.push({ entry, matchIndex: idx });
    } else {
      // Check if the match begins at a word boundary
      const charBefore = entry.normalized[idx - 1];
      const isWordBoundary = charBefore === " " || charBefore === "-" || charBefore === "'";

      if (isWordBoundary) {
        wordStartsWith.push({ entry, matchIndex: idx });
      } else {
        contains.push({ entry, matchIndex: idx });
      }
    }
  }

  return [...startsWith, ...wordStartsWith, ...contains].slice(0, MAX_SUGGESTIONS);
}


// --- DOM References ---

const inputEl = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-btn");
const suggestionsEl = document.getElementById("suggestions-list");
const infoBar = document.getElementById("info-bar");

let activeIndex = -1;
let currentResults = [];


// --- Rendering ---

/**
 * Highlight the matched substring within the country name.
 * Returns an HTML string with the match wrapped in a <mark> element.
 */
function highlightMatch(name, matchIndex, queryLength) {
  const before = name.slice(0, matchIndex);
  const match = name.slice(matchIndex, matchIndex + queryLength);
  const after = name.slice(matchIndex + queryLength);
  return `${escapeHtml(before)}<mark class="match-highlight">${escapeHtml(match)}</mark>${escapeHtml(after)}`;
}

/** Basic HTML escape to prevent XSS. */
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/**
 * Map the normalized match index back to the original (non-normalized) string.
 * Since NFD decomposition can expand characters (e.g., a -> a + combining mark),
 * we walk through the original string to find the correct position.
 */
function mapIndexToOriginal(original, normalizedIndex) {
  let normPos = 0;
  let origPos = 0;
  const normStr = normalize(original);

  while (normPos < normalizedIndex && origPos < original.length) {
    // Advance through the original string one character at a time,
    // counting how many normalized characters that corresponds to.
    const origChar = original[origPos];
    const origCharNorm = normalize(origChar);
    normPos += origCharNorm.length;
    origPos++;
  }
  return origPos;
}

/**
 * Calculate the length in the original string that corresponds to
 * a given length in the normalized string, starting from origStart.
 */
function mapLengthToOriginal(original, origStart, normalizedLength) {
  let normConsumed = 0;
  let origPos = origStart;

  while (normConsumed < normalizedLength && origPos < original.length) {
    const origChar = original[origPos];
    const origCharNorm = normalize(origChar);
    normConsumed += origCharNorm.length;
    origPos++;
  }
  return origPos - origStart;
}

function renderSuggestions(results, queryLength) {
  currentResults = results;
  activeIndex = -1;

  if (results.length === 0) {
    suggestionsEl.innerHTML = '<li class="no-results">No matching countries found</li>';
    suggestionsEl.classList.add("open");
    inputEl.setAttribute("aria-expanded", "true");
    infoBar.textContent = "0 results";
    return;
  }

  suggestionsEl.innerHTML = results
    .map((r, i) => {
      const origMatchStart = mapIndexToOriginal(r.entry.name, r.matchIndex);
      const origMatchLength = mapLengthToOriginal(r.entry.name, origMatchStart, queryLength);

      const highlighted = highlightMatch(r.entry.name, origMatchStart, origMatchLength);
      return `<li class="suggestion-item" role="option" data-index="${i}" id="suggestion-${i}">
        <span class="country-id">#${r.entry.id}</span>
        <span class="country-name">${highlighted}</span>
      </li>`;
    })
    .join("");

  suggestionsEl.classList.add("open");
  inputEl.setAttribute("aria-expanded", "true");
  infoBar.textContent = `${results.length} result${results.length === 1 ? "" : "s"}`;
}

function hideSuggestions() {
  suggestionsEl.classList.remove("open");
  suggestionsEl.innerHTML = "";
  inputEl.setAttribute("aria-expanded", "false");
  activeIndex = -1;
  currentResults = [];
}

function setActiveItem(index) {
  const items = suggestionsEl.querySelectorAll(".suggestion-item");
  items.forEach((item) => item.classList.remove("active"));
  activeIndex = index;

  if (index >= 0 && index < items.length) {
    items[index].classList.add("active");
    items[index].scrollIntoView({ block: "nearest" });
    inputEl.setAttribute("aria-activedescendant", `suggestion-${index}`);
  } else {
    inputEl.removeAttribute("aria-activedescendant");
  }
}

function selectItem(index) {
  if (index >= 0 && index < currentResults.length) {
    inputEl.value = currentResults[index].entry.name;
    hideSuggestions();
    clearBtn.classList.add("visible");
    infoBar.textContent = `Selected: ${currentResults[index].entry.name}`;
  }
}


// --- Event Handlers ---

inputEl.addEventListener("input", () => {
  const query = inputEl.value;

  // Show/hide clear button
  clearBtn.classList.toggle("visible", query.length > 0);

  if (!query.trim()) {
    hideSuggestions();
    infoBar.textContent = "";
    return;
  }

  const results = search(query);
  renderSuggestions(results, normalize(query.trim()).length);
});

inputEl.addEventListener("keydown", (e) => {
  if (!suggestionsEl.classList.contains("open")) return;

  const itemCount = currentResults.length;

  switch (e.key) {
    case "ArrowDown":
      e.preventDefault();
      setActiveItem(activeIndex < itemCount - 1 ? activeIndex + 1 : 0);
      break;

    case "ArrowUp":
      e.preventDefault();
      setActiveItem(activeIndex > 0 ? activeIndex - 1 : itemCount - 1);
      break;

    case "Enter":
      e.preventDefault();
      if (activeIndex >= 0) {
        selectItem(activeIndex);
      }
      break;

    case "Escape":
      hideSuggestions();
      break;
  }
});

suggestionsEl.addEventListener("mousedown", (e) => {
  // Prevent input blur
  e.preventDefault();
});

suggestionsEl.addEventListener("click", (e) => {
  const item = e.target.closest(".suggestion-item");
  if (item) {
    selectItem(parseInt(item.dataset.index, 10));
  }
});

clearBtn.addEventListener("click", () => {
  inputEl.value = "";
  hideSuggestions();
  clearBtn.classList.remove("visible");
  infoBar.textContent = "";
  inputEl.focus();
});

// Close dropdown when clicking outside
document.addEventListener("click", (e) => {
  if (!document.getElementById("search-wrapper").contains(e.target)) {
    hideSuggestions();
  }
});

// Show results again when focusing back on the input
inputEl.addEventListener("focus", () => {
  const query = inputEl.value;
  if (query.trim()) {
    const results = search(query);
    renderSuggestions(results, normalize(query.trim()).length);
  }
});
