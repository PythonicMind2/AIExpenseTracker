# Changelog

All notable changes to **Expense Tracker Pro Web** are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

### Planned
- Google Sheets sync
- Spending predictions / forecasts
- CSV import
- Custom category creation
- Mobile PWA support

---

## [1.0.0] — 2025-03-04

### Added
- **Multi-user login system** — register/sign-in, per-user data isolation, hashed passwords via Werkzeug
- **8-tab SPA** — Dashboard, Add, Expenses, Charts, History, Budget, Recurring, Settings
- **AI Chatbot** — Gemini 2.0 Flash powered assistant with full expense context; no SDK required (pure `urllib`)
- **5 chart types** — Pie, Monthly Bar, Category Compare, Daily Line, Top-5 Donut (Chart.js)
- **Recurring expenses** — Daily / Weekly / Bi-weekly / Monthly / Yearly, auto-applied on app start
- **12 currencies** — live symbol switching across all views, persisted per user
- **PDF export** — rich formatted report: KPIs, category table, budget status, full expense log (ReportLab)
- **CSV + XLSX export** — filtered data with auto-generated summary sheet
- **Budget tracker** — per-category monthly budgets with colour-coded progress bars
- **Dark / Light theme** — Warm Forest (light) + GitHub Dark, persisted per user
- **Smart launcher** (`run.py`) — finds a free port, auto-opens browser, works frozen as `.exe`
- **GitHub Actions CI** — syntax + import check on Python 3.9–3.12
- **Issue templates** — bug report and feature request forms
- **MIT License**, **CONTRIBUTING.md**, **CHANGELOG.md**

### Tech
- Flask 3.x, Werkzeug 3.x, Pandas, OpenPyXL, ReportLab
- Chart.js 4.4 (CDN), Outfit + Syne fonts (Google Fonts CDN)
- All data stored locally in `~/.expense_tracker_web/`
- Gemini API called via plain `urllib` — zero extra AI dependencies
