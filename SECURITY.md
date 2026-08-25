# Security Policy

## Public repository boundary

This repository contains only a sanitized reconstruction and synthetic data.

Never commit:

- `.env` files;
- OAuth client secrets or API keys;
- Bearer/JWT tokens;
- real CVs or OCR outputs;
- production database files (`*.db`, `*.sqlite*`);
- logs, Power BI exports or raw source exports;
- internal URLs, tenant identifiers or SSH configuration.

## Secrets

Configuration must be supplied through environment variables or an external secret manager. `.env.example` contains names only.

## Docker

The public demo:

- runs as a non-root user;
- drops Linux capabilities;
- enables `no-new-privileges`;
- uses a read-only root filesystem;
- does not expose ports;
- runs without network access by default.

The OCR image requires writable temporary storage for LibreOffice/Tesseract and therefore uses a dedicated `tmpfs` for `/tmp`.

## Release check

Before any public push:

```bash
python scripts/public_release_check.py
```

Then inspect the exact Git staging set:

```bash
git diff --cached --name-only
```
