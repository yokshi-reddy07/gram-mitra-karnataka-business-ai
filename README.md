# Gram Mitra — Karnataka Business AI

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Important
- Delete the old `financial_planner.html`; this rebuild intentionally does not use it.
- This version fixes the common Jinja `user is undefined` problem by passing `user=current_user()` to rendered pages.
- Sign up/login uses SQLite and Werkzeug password hashing.
- Reports are stored in browser localStorage until replaced by a new analysis.
- Financing/scheme figures are advisory estimates and must be verified against current official sources and lender terms.
