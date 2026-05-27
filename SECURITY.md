# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project (e.g. a flaw in the ingest scripts, CI pipeline, or published package), please report it responsibly.

**Do not open a public issue.** Instead, email [emmanuelgjr@gmail.com](mailto:emmanuelgjr@gmail.com) with:

- A description of the vulnerability
- Steps to reproduce
- Any relevant logs or screenshots

You should receive an acknowledgement within 48 hours. Fixes for confirmed vulnerabilities will be released as soon as practical, and you will be credited in the changelog unless you prefer otherwise.

## Scope

This policy covers:

- The `genai-incidents` Python package published on PyPI
- The ingest and build scripts under `scripts/`
- The GitHub Actions workflows under `.github/workflows/`
- The static site served via GitHub Pages

Data quality issues (incorrect incident classification, missing fields, etc.) are not security vulnerabilities — please file a regular issue for those.

## Supported Versions

Only the latest release on the `main` branch is actively maintained.
