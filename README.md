<div align="center">

<img src="https://raw.githubusercontent.com/YOUR_USERNAME/expense-tracker-pro-web/main/screenshots/banner.png" alt="Expense Tracker Pro" width="100%">

# 💸 Expense Tracker Pro — Web

**A full-featured personal finance web app powered by Flask + Gemini AI**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

[Features](#-features) · [Quick Start](#-quick-start) · [AI Chatbot](#-ai-chatbot) · [Screenshots](#-screenshots) · [Contributing](#-contributing)

</div>

---

## ✨ Features

| | Feature | Description |
|--|---------|-------------|
| 📊 | **Dashboard** | KPI cards, 6-month trend chart, category breakdown |
| ➕ | **Add Expense** | Log amount, description, category, date, notes |
| 📋 | **Expenses Table** | Search, filter, sort, multi-select bulk delete |
| 📈 | **Charts** | Pie, bar, line, donut — 5 chart types via Chart.js |
| 📅 | **History** | Browse by month or year with category summaries |
| 🎯 | **Budget Tracker** | Per-category budgets with live progress bars |
| 🔁 | **Recurring** | Auto-posting daily/weekly/monthly/yearly rules |
| 🤖 | **AI Chatbot** | Gemini-powered assistant with full access to your data |
| 🔐 | **Multi-user Login** | Register/sign-in, all data isolated per user |
| 🌙 | **Dark / Light Theme** | One-click toggle, persists across sessions |
| 💱 | **12 Currencies** | ₹ INR · $ USD · € EUR · £ GBP · ¥ JPY and more |
| 📤 | **Export** | CSV · XLSX · PDF reports with budgets & KPIs |

---

## 🤖 AI Chatbot

The built-in AI assistant is powered by **Google Gemini 2.0 Flash** and has full read access to your expense data on every message. Ask it anything:

> *"How much did I spend on food this month?"*
> *"Which category is over budget?"*
> *"Compare my last 3 months and give me saving tips"*
> *"What's my biggest expense this year?"*

**Setup:** Get a free API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → paste it in ⚙️ Settings. The key is stored locally and never shared with anyone except Google's API.

> **Note:** All app features work offline. Only the AI chat requires internet.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** — [python.org](https://python.org)

### 1 — Clone
```bash
git clone https://github.com/YOUR_USERNAME/expense-tracker-pro-web.git
cd expense-tracker-pro-web
```

### 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### 3 — Run
```bash
python run.py
```

The app opens automatically at **http://localhost:5000**. Create an account on first launch.

> **Tip:** Use `python app.py` for debug mode with hot-reload during development.

---

## 📁 Project Structure

```
expense-tracker-pro-web/
│
├── app.py                  ← Flask backend — all routes & Gemini API
├── run.py                  ← Launcher (auto-opens browser, finds free port)
├── requirements.txt
│
├── templates/
│   ├── index.html          ← Main SPA (all 8 tabs + AI chat panel)
│   └── login.html          ← Login / register page
│
├── static/
│   └── css/
│       └── style.css       ← Full design system (light + dark themes)
│
└── .github/
    ├── workflows/
    │   └── ci.yml          ← Lint + syntax check on push/PR
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## 💾 Data Storage

All data is stored **locally** on your machine — never in the cloud.

```
~/.expense_tracker_web/
├── users.json                  ← Hashed credentials
└── users/
    └── <username>/
        ├── expenses.json
        ├── budgets.json
        ├── recurring.json
        └── settings.json       ← Theme, currency, Gemini key
```

**Backup:** copy `~/.expense_tracker_web/`  
**Reset:** delete it

---

## 🎨 Themes

| ☀️ Light — Warm Forest | 🌙 Dark — GitHub Dark |
|---|---|
| Cream `#F5F0E8` · Forest green accent | Ink `#0D1117` · Electric blue accent |

---

## 💱 Currencies

`₹ INR` · `$ USD` · `€ EUR` · `£ GBP` · `¥ JPY` · `¥ CNY` · `A$ AUD` · `C$ CAD` · `CHF` · `S$ SGD` · `AED` · `SAR`

---

## 🔧 Development

```bash
# Run in debug mode (hot reload)
python app.py

# Run tests / syntax check
python -m py_compile app.py run.py
```

**Adding a new chart type:**  edit `renderCharts()` in `index.html` and add a new `/api/charts` case in `app.py`.

**Adding a new currency:** add to the `CURRENCIES` dict in `app.py` and the `currencySymbol()` map in `index.html`.

---

## 🤝 Contributing

All contributions welcome — bug fixes, new features, UI tweaks, translations.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

```bash
git checkout -b feature/your-feature
# ... make changes ...
git commit -m "feat: describe your change"
git push origin feature/your-feature
# open a Pull Request
```

---

## 📋 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `werkzeug` | Password hashing, WSGI utilities |
| `pandas` | Data manipulation & CSV/XLSX export |
| `openpyxl` | Excel file writing |
| `reportlab` | PDF report generation |
| Gemini REST API | AI chatbot (via `urllib`, no SDK needed) |
| Chart.js (CDN) | All charts in the browser |
| Google Fonts (CDN) | Outfit + Syne typefaces |


---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️, Python, and a lot of ☕

</div>
