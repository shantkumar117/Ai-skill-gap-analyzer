# Production Deployment — What a Real App Requires

## The Hard Truth
This app uses SQLite (`database/skill_gap.db`). On Vercel, the filesystem resets on every deploy and cold-start. Your users' analyses will vanish. That is not acceptable for a real production app.

## Required Changes Before Going Live

### 1. Persistent Database (non-negotiable)
- Replace SQLite with **PostgreSQL via Neon / Supabase / PlanetScale**.
- Update `database.py` `get_connection()` to use `psycopg2` / SQLAlchemy instead of `sqlite3`.
- Migrate `AuthUsers`, `Analysis`, `Skills`, `RoleSkills`, `UserSkills`.

### 2. Account Recovery (what you asked for)
- Add `email` to `AuthUsers`.
- Add `PasswordReset` table: `token`, `user_id`, `expires_at`, `used`.
- Routes:
  - `/forgot-username` — enter email → show username masked (or require login after verification).
  - `/forgot-password` — enter email → send reset link (token + 1-hour expiry).
  - `/reset-password/<token>` — validate token → set new password.
- Rate-limit to 3 attempts / IP / hour.
- Use `secrets.token_urlsafe()` for tokens; never expose tokens in URLs after use.

### 3. Security Hardening
- `SECRET_KEY` from env only (`os.getenv('SECRET_KEY')`). Never commit.
- `.env` in `.gitignore`.
- `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`.
- HTTPS redirect (Flask `before_request` or Vercel config).
- Add CSP headers; sanitize all user inputs (already partially done with `normalize_skills`).

### 4. Email Service
- Configure Brevo SMTP with `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`, and optionally `BREVO_REPLY_TO_EMAIL`.
- Use only a sender address and domain verified in Brevo.
- Store email credentials in Vercel's Environment Variables, never in the repository.
- Never log email contents or API keys.

### 5. What I Implemented Now (practical partial fix)
- `database.py`: `try/finally connection.close()` enforced on every DB path; `timeout=10.0`; fixed `UNIQUE` crash from `save_analysis()` overwriting username.
- `app.py`: env-backed `SECRET_KEY`; `/robots.txt` + `/sitemap.xml`; init/purge at import; `vercel.json`.
- `templates/profile.html`: singular case fixed (`Expires in X day`); `delete` + `keep` confirmed working.
- `templates/index.html` + `about.html`: expanded SEO content + FAQ structured data.

### 6. What Is Still Missing (do not deploy without these)
- **Real DB migration** (SQLite → Postgres).
- **Forgot-username / forgot-password routes + Brevo email sending** (needs verified sender configuration + DB table).
- **Rate limiting** on auth routes (use Flask-Limiter or in-memory per-IP).
- **Password-reset token table and Brevo email template**.
- **HTTPS / secure cookie settings**.
- **Actual `.env` with production secrets** committed to Vercel dashboard (not repo).

## Bottom Line
A "real web app" means: persistent data, recoverable accounts, secret management, HTTPS, and no filesystem dependence. The current code is correct for a student/demo project; for production, migrate DB, add email + reset flow, and move secrets to Vercel env. Do not deploy SQLite to Vercel and expect users to keep their data.
