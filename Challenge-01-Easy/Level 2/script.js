/**
 * Interactive Scientific Calculator - GDG Algiers Level 2
 * Built with Vanilla JavaScript (No Frameworks).
 * Features:
 * - Dijkstra's Shunting-Yard Algorithm for strict Operator Precedence (BODMAS / PEMDAS)
 * - Exponentiation (^), Modulo (%), Parentheses (()), and Unary Negation (+/-)
 * - Full Physical Keyboard Support with active visual feedback
 * - Calculation History with LocalStorage persistence
 */

// --- Calculator State ---
let currentExpression = '';
let lastAnswer = null;
let lastResultCalculated = false;
let historyItems = [];

// --- DOM Elements ---
const screenHistory = document.getElementById('screen-history');
const screenMain = document.getElementById('screen-main');
const historyList = document.getElementById('history-list');
const btnClearHistory = document.getElementById('btn-clear-history');
const btnToggleHistory = document.getElementById('btn-toggle-history');
const historyPanel = document.getElementById('history-panel');

// --- Initialization ---
function init() {
  loadHistoryFromStorage();
  bindButtonEvents();
  bindKeyboardEvents();
  updateScreen();
}

// --- Screen Updates ---
function updateScreen(result = null, isError = false) {
  if (isError) {
    screenMain.classList.add('has-error');
    screenMain.textContent = result || 'Error';
    return;
  }

  screenMain.classList.remove('has-error');

  if (result !== null) {
    screenMain.textContent = formatNumber(result);
    screenHistory.textContent = currentExpression + ' =';
  } else {
    screenMain.textContent = currentExpression || '0';
    screenHistory.textContent = lastResultCalculated && lastAnswer !== null ? `Ans = ${formatNumber(lastAnswer)}` : '';
  }

  // Auto scroll right on overflow
  screenMain.scrollLeft = screenMain.scrollWidth;
}

function formatNumber(num) {
  if (typeof num !== 'number' || isNaN(num)) return num;
  // Eliminate floating point precision issues like 0.1 + 0.2 = 0.30000000000000004
  const rounded = parseFloat(num.toFixed(10));
  // Format with commas for readability if finite integer/decimal
  if (Math.abs(rounded) >= 1e12 || (Math.abs(rounded) < 1e-6 && rounded !== 0)) {
    return rounded.toExponential(6);
  }
  return rounded.toString();
}

// --- Expression Tokenizer ---
function tokenize(expr) {
  const tokens = [];
  let i = 0;
  const cleanExpr = expr.replace(/\s+/g, '');

  while (i < cleanExpr.length) {
    const ch = cleanExpr[i];

    // Numbers (integer or decimal)
    if (/\d/.test(ch) || (ch === '.' && /\d/.test(cleanExpr[i + 1] || ''))) {
      let numStr = '';
      let hasDot = false;
      while (i < cleanExpr.length && (/\d/.test(cleanExpr[i]) || (cleanExpr[i] === '.' && !hasDot))) {
        if (cleanExpr[i] === '.') hasDot = true;
        numStr += cleanExpr[i++];
      }
      tokens.push({ type: 'number', value: parseFloat(numStr) });
      continue;
    }

    // Unary Minus: if '-' is at start, or preceded by an operator or '('
    if (ch === '-') {
      const prev = tokens[tokens.length - 1];
      if (!prev || prev.type === 'operator' || prev.type === 'unary' || prev.value === '(') {
        tokens.push({ type: 'unary', value: 'u-' });
        i++;
        continue;
      }
    }

    // Binary Operators
    if ('+-*/%^'.includes(ch)) {
      tokens.push({ type: 'operator', value: ch });
      i++;
      continue;
    }

    // Parentheses
    if (ch === '(' || ch === ')') {
      tokens.push({ type: 'paren', value: ch });
      i++;
      continue;
    }

    // Unknown character, skip
    i++;
  }

  return tokens;
}

// --- Shunting-Yard Parser & Evaluator ---
function evaluateExpression(expr) {
  if (!expr || expr.trim() === '') return 0;

  const tokens = tokenize(expr);
  if (tokens.length === 0) return 0;

  // Precedence and Associativity Rules
  const precedence = {
    'u-': 5,
    '^': 4,
    '*': 3,
    '/': 3,
    '%': 3,
    '+': 2,
    '-': 2
  };

  const associativity = {
    'u-': 'right',
    '^': 'right',
    '*': 'left',
    '/': 'left',
    '%': 'left',
    '+': 'left',
    '-': 'left'
  };

  const outputQueue = [];
  const operatorStack = [];

  for (const token of tokens) {
    if (token.type === 'number') {
      outputQueue.push(token.value);
    } else if (token.type === 'operator' || token.type === 'unary') {
      const o1 = token.value;
      while (operatorStack.length > 0) {
        const o2 = operatorStack[operatorStack.length - 1];
        if (o2 === '(') break;

        const p1 = precedence[o1] || 0;
        const p2 = precedence[o2] || 0;
        const assoc = associativity[o1] || 'left';

        if ((assoc === 'left' && p1 <= p2) || (assoc === 'right' && p1 < p2)) {
          outputQueue.push(operatorStack.pop());
        } else {
          break;
        }
      }
      operatorStack.push(o1);
    } else if (token.value === '(') {
      operatorStack.push('(');
    } else if (token.value === ')') {
      while (operatorStack.length > 0 && operatorStack[operatorStack.length - 1] !== '(') {
        outputQueue.push(operatorStack.pop());
      }
      if (operatorStack.length > 0 && operatorStack[operatorStack.length - 1] === '(') {
        operatorStack.pop(); // Remove matching '('
      }
    }
  }

  while (operatorStack.length > 0) {
    const op = operatorStack.pop();
    if (op !== '(' && op !== ')') {
      outputQueue.push(op);
    }
  }

  // --- RPN Evaluation ---
  const evalStack = [];

  for (const item of outputQueue) {
    if (typeof item === 'number') {
      evalStack.push(item);
    } else if (item === 'u-') {
      const a = evalStack.pop();
      if (a === undefined) throw new Error('Syntax Error');
      evalStack.push(-a);
    } else {
      const b = evalStack.pop();
      const a = evalStack.pop();
      if (a === undefined || b === undefined) throw new Error('Syntax Error');

      let res;
      switch (item) {
        case '+':
          res = a + b;
          break;
        case '-':
          res = a - b;
          break;
        case '*':
          res = a * b;
          break;
        case '/':
          if (b === 0) throw new Error('Cannot divide by 0');
          res = a / b;
          break;
        case '%':
          if (b === 0) throw new Error('Cannot modulo by 0');
          res = a % b;
          break;
        case '^':
          res = Math.pow(a, b);
          break;
        default:
          throw new Error('Unknown Operator');
      }
      evalStack.push(res);
    }
  }

  if (evalStack.length !== 1 || isNaN(evalStack[0])) {
    throw new Error('Syntax Error');
  }

  return evalStack[0];
}

// --- Action Handlers ---

function appendValue(val) {
  if (lastResultCalculated) {
    // If user inputs an operator right after a calculation, chain from last answer
    if ('+-*/%^'.includes(val)) {
      currentExpression = (lastAnswer !== null ? formatNumber(lastAnswer) : '0') + ' ' + val + ' ';
    } else {
      currentExpression = val;
    }
    lastResultCalculated = false;
  } else {
    // Clean spacing around operators
    if ('+-*/%^'.includes(val)) {
      currentExpression += ' ' + val + ' ';
    } else {
      currentExpression += val;
    }
  }
  updateScreen();
}

function handleBackspace() {
  if (lastResultCalculated) {
    clearAll();
    return;
  }
  currentExpression = currentExpression.trimEnd();
  currentExpression = currentExpression.slice(0, -1).trimEnd();
  updateScreen();
}

function clearAll() {
  currentExpression = '';
  lastResultCalculated = false;
  updateScreen();
}

function handleNegate() {
  if (!currentExpression && lastAnswer !== null) {
    currentExpression = formatNumber(-lastAnswer);
    lastResultCalculated = false;
    updateScreen();
    return;
  }

  // Find the last number token in currentExpression and toggle sign
  const match = currentExpression.match(/(-?\d+\.?\d*)$/);
  if (match) {
    const num = match[0];
    const negated = num.startsWith('-') ? num.slice(1) : '-' + num;
    currentExpression = currentExpression.slice(0, match.index) + negated;
    updateScreen();
  } else {
    currentExpression += '-';
    updateScreen();
  }
}

function handleCalculate() {
  if (!currentExpression.trim()) return;

  try {
    const result = evaluateExpression(currentExpression);
    saveHistory(currentExpression, result);
    lastAnswer = result;
    lastResultCalculated = true;
    updateScreen(result, false);
  } catch (err) {
    updateScreen(err.message || 'Syntax Error', true);
  }
}

function handleAns() {
  if (lastAnswer === null) return;
  appendValue(formatNumber(lastAnswer));
}

// --- History Management ---

function saveHistory(expr, result) {
  const item = {
    id: Date.now(),
    expression: expr,
    result: formatNumber(result)
  };
  historyItems.unshift(item);
  if (historyItems.length > 50) historyItems.pop(); // keep last 50
  saveHistoryToStorage();
  renderHistory();
}

function renderHistory() {
  if (historyItems.length === 0) {
    historyList.innerHTML = '<p class="history-empty">No calculations yet. Enter an expression and hit =</p>';
    return;
  }

  historyList.innerHTML = historyItems.map(item => `
    <div class="history-item" data-expr="${item.expression}" data-res="${item.result}">
      <span class="history-item-expr">${escapeHtml(item.expression)} =</span>
      <span class="history-item-res">${escapeHtml(item.result)}</span>
    </div>
  `).join('');

  // Add click to restore history
  historyList.querySelectorAll('.history-item').forEach(el => {
    el.addEventListener('click', () => {
      currentExpression = el.getAttribute('data-expr');
      lastResultCalculated = false;
      updateScreen();
    });
  });
}

function clearHistory() {
  historyItems = [];
  saveHistoryToStorage();
  renderHistory();
}

function saveHistoryToStorage() {
  try {
    localStorage.setItem('gdg_calc_history', JSON.stringify(historyItems));
  } catch (e) {
    // Ignore storage quota errors
  }
}

function loadHistoryFromStorage() {
  try {
    const saved = localStorage.getItem('gdg_calc_history');
    if (saved) historyItems = JSON.parse(saved);
  } catch (e) {
    historyItems = [];
  }
  renderHistory();
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// --- Event Binding ---

function bindButtonEvents() {
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const val = btn.getAttribute('data-value');
      const action = btn.getAttribute('data-action');

      if (val !== null) {
        appendValue(val);
      } else if (action === 'clear') {
        clearAll();
      } else if (action === 'backspace') {
        handleBackspace();
      } else if (action === 'calculate') {
        handleCalculate();
      } else if (action === 'toggle-sign') {
        handleNegate();
      } else if (action === 'ans') {
        handleAns();
      }
    });
  });

  if (btnClearHistory) {
    btnClearHistory.addEventListener('click', clearHistory);
  }

  if (btnToggleHistory && historyPanel) {
    btnToggleHistory.addEventListener('click', () => {
      historyPanel.classList.toggle('hidden');
    });
  }
}

function bindKeyboardEvents() {
  window.addEventListener('keydown', (e) => {
    // Prevent accidental form submit or scrolling on space
    if (e.key === ' ' || e.key === 'Tab') return;

    let targetButton = null;

    if (/\d/.test(e.key)) {
      targetButton = document.querySelector(`.btn[data-value="${e.key}"]`);
      appendValue(e.key);
    } else if (e.key === '.') {
      targetButton = document.querySelector('.btn[data-value="."]');
      appendValue('.');
    } else if (['+', '-', '*', '/', '^', '%', '(', ')'].includes(e.key)) {
      targetButton = document.querySelector(`.btn[data-value="${e.key}"]`);
      appendValue(e.key);
    } else if (e.key === 'Enter' || e.key === '=') {
      e.preventDefault();
      targetButton = document.querySelector('.btn[data-action="calculate"]');
      handleCalculate();
    } else if (e.key === 'Backspace') {
      targetButton = document.querySelector('.btn[data-action="backspace"]');
      handleBackspace();
    } else if (e.key === 'Escape' || e.key.toLowerCase() === 'c') {
      targetButton = document.querySelector('.btn[data-action="clear"]');
      clearAll();
    }

    // Visual feedback on physical key press
    if (targetButton) {
      targetButton.classList.add('active-key');
      setTimeout(() => targetButton.classList.remove('active-key'), 130);
    }
  });
}

// Start application
init();
