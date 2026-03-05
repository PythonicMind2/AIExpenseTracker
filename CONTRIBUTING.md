# Contributing to Expense Tracker Pro Web

Thank you for your interest in contributing! 🎉  
All kinds of contributions are welcome — bug reports, feature ideas, code, docs, and design improvements.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Guidelines](#pull-request-guidelines)

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/expense-tracker-pro-web.git
   cd expense-tracker-pro-web
   ```
3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .venv\Scripts\activate       # Windows
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run in dev mode** (hot reload):
   ```bash
   python app.py
   ```

---

## Reporting Bugs

Search [existing issues](../../issues) first, then open a [Bug Report](../../issues/new?template=bug_report.md).

Please include:
- What happened vs. what you expected
- Steps to reproduce
- OS + Python version
- Any error messages / tracebacks

---

## Requesting Features

Open a [Feature Request](../../issues/new?template=feature_request.md) with:
- The problem you're solving
- Your proposed solution
- Alternatives you considered

---

## Development Workflow

```bash
# Branch naming
git checkout -b feature/my-feature      # new features
git checkout -b fix/some-bug            # bug fixes
git checkout -b docs/improve-readme     # docs only
git checkout -b style/typography        # CSS/UI changes

# After coding
git add .
git commit -m "feat: add dark mode for chat panel"
git push origin feature/my-feature
# → open a Pull Request on GitHub
```

---

## Code Style

**Python (`app.py`, `run.py`)**
- Follow **PEP 8** — 4-space indentation, max ~100 chars per line
- Type hints where practical
- Docstrings on public functions

**File responsibilities — don't mix concerns:**

| File | Owns |
|------|------|
| `app.py` | Flask routes, business logic, Gemini API |
| `run.py` | Process launcher only |
| `templates/index.html` | All UI + client-side JS |
| `templates/login.html` | Auth UI only |
| `static/css/style.css` | All styles — no inline styles in HTML |

**CSS**
- Use CSS variables (`--accent`, `--text2`, etc.) — never hardcode colours
- Add new components in clearly labelled sections
- Both light and dark theme must work for every new element

**JavaScript**
- Plain vanilla JS, no frameworks
- All API calls through `fetch()` using the existing pattern
- Update `chatHistory` for any new AI-related feature

---

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Google Sheets export
fix: recurring expense not applying on weekends
docs: add screenshots to README
style: increase font sizes in budget tab
refactor: extract chart helpers into separate functions
test: add syntax check for app.py
chore: update reportlab to 4.1
```

---

## Pull Request Guidelines

- **One PR per feature or fix** — keep them focused
- **Reference the issue** your PR closes: `Closes #42`
- Briefly describe what changed and why in the PR description
- The app must **start and run without errors**
- Both **light and dark themes** must look correct for UI changes
- CI must pass

---

Thanks again! ⭐
