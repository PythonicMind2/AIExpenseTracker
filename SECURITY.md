# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## What is stored locally

This app stores all user data **only on the local machine** in `~/.expense_tracker_web/`.

- Passwords are hashed using **Werkzeug's `generate_password_hash`** (PBKDF2-SHA256). Plain-text passwords are never written to disk.
- Your Gemini API key is stored in your own `settings.json` file. It is sent **only to `generativelanguage.googleapis.com`** during AI chat requests — never anywhere else.
- No analytics, telemetry, or third-party tracking of any kind.

## Reporting a Vulnerability

If you find a security issue, please **do not open a public issue**.

Instead, email the maintainer directly or open a [GitHub Security Advisory](../../security/advisories/new) (private).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

You can expect a response within 72 hours.
