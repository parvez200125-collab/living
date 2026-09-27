# LivingWay 3D — Website + Admin Dashboard Package

## What is included
- `public/` — LivingWay 3D public website and `/admin/` login/dashboard interface.
- `python-backend/` — FastAPI API starter with SQLite record storage and server-verified admin sessions.
- `ORIGINAL-FRONTEND-BACKUP.zip` — backup of the original public frontend included with this package.

The public website files/design were retained from the supplied package. The dashboard UI follows the LivingWay 3D blue/navy/white visual direction.

## Important — read before deploying
This ZIP is a **starter package**, not a verified, production-ready live deployment. It has not been deployed to or tested against your Cloudflare account/live domain.

The backend in this ZIP is **Python FastAPI**. It cannot be deployed with `wrangler deploy` as a Cloudflare Worker. Cloudflare Workers run a different runtime. To use this exact backend, deploy it to a Python-capable host (for example, a suitable app host/VPS) with persistent storage, then configure your domain/routing. Cloudflare Pages/Workers alone will not run this Python backend.

Some dashboard sections store administrative records/metadata only. Payment gateway processing, generated PDF invoices, customer self-service portal, private file uploads/downloads, customer-facing message delivery, email-based password reset, and legally binding e-signatures are not implemented as complete production integrations. Do not enter real payment-card data or sensitive customer documents into this starter.

## Local test on Windows (CMD)

1. Install Node.js only if needed for other frontend tooling; for this Python backend, install Python 3.11+.
2. Extract this ZIP.
3. Open the extracted `LivingWay-3D-Admin-Package\python-backend` folder.
4. Click the File Explorer address bar, type `cmd`, and press Enter.
5. Run:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

6. Set two admin accounts and a long session secret in the same CMD window:

```bat
set ADMIN1_EMAIL=admin1@example.com
set ADMIN1_PASSWORD=ReplaceWithAUniqueStrongPassword
set ADMIN2_EMAIL=admin2@example.com
set ADMIN2_PASSWORD=ReplaceWithAnotherUniqueStrongPassword
set SESSION_SECRET=ReplaceWithASeparateRandomSecretAtLeast32Characters
set COOKIE_SECURE=false
```

Replace the sample credentials with your own. Do not share passwords or commit them to source control.

7. Start the backend:

```bat
uvicorn main:app --host 127.0.0.1 --port 8000
```

8. Open these in your browser:
- Public website: `http://127.0.0.1:8000/`
- Admin login: `http://127.0.0.1:8000/admin/`
- Health check: `http://127.0.0.1:8000/api/health`

Keep the CMD window open while testing. Stop the server with `Ctrl+C`.

## Before any live deployment
- Deploy to a separate staging environment first.
- Configure persistent database storage (`DATABASE_PATH`) and set `COOKIE_SECURE=true` on HTTPS.
- Set unique credentials for exactly two authorized admins and a strong, separate `SESSION_SECRET`.
- Test login/logout, wrong-password rejection, API access without a session, record creation/editing, request submission, and persistence after restart.
- Back up the current production website before changing DNS, routes, or deployment settings.
- Do not replace the existing `design3.livingwayd2.workers.dev` deployment until the backend/runtime and routing are deliberately migrated and tested.

## Troubleshooting
- `Failed to execute 'json' on 'Response': Unexpected end of JSON input` usually means the frontend received an empty or non-JSON response (for example, the API route is not running or a static host served an error page). Confirm the FastAPI server is running and open `/api/health` first.
- If login says server setup is incomplete, verify all five environment variables in the same terminal session where Uvicorn is started.
- On HTTPS hosting, use `COOKIE_SECURE=true`; for local HTTP testing, use `COOKIE_SECURE=false`.

## Security notes
- Never send passwords, Cloudflare API tokens, or session secrets in chat.
- Use HTTPS in production.
- This starter is not a substitute for a security review, rate limiting, CSRF protection, backups, monitoring, and production testing.
