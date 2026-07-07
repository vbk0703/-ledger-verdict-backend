# Ledger & Verdict — backend proxy

Fixes "Failed to fetch": FMP doesn't send CORS headers, so a browser
calling it directly gets blocked. This tiny FastAPI server calls FMP
for you and returns clean JSON with CORS enabled.

## Fastest path: Render.com (free tier)

1. Create a new GitHub repo, add `main.py` and `requirements.txt` from this folder, push.
2. Go to render.com → New → Web Service → connect that repo.
3. Settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Under "Environment", add:
   - `FMP_API_KEY` = your Financial Modeling Prep key
5. Deploy. Render gives you a URL like `https://ledger-verdict.onrender.com`.
6. Paste that URL into the frontend's "Backend URL" field and run a ticker.

Note: Render's free tier sleeps after 15 min idle — first request after
a break takes ~30s to wake up. That's normal, not a bug.

## Run it locally instead (for testing before you deploy)

```bash
pip install fastapi uvicorn httpx --break-system-packages
export FMP_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

Then put `http://localhost:8000` in the frontend's Backend URL field.
(This only works if you also open the frontend file locally in the
same browser — it won't reach localhost from the Claude chat preview.)

## Alternatives to Render

- **Railway.app** — same idea, similarly generous free tier.
- **Fly.io** — free tier, a bit more setup (needs a `Dockerfile` or `fly.toml`).
- **Vercel** — works if you convert `main.py` into a Vercel serverless
  function instead of a long-running FastAPI app (different structure,
  ask if you want that version).

## Health check

Once deployed, visit `https://your-app.onrender.com/api/health` — it
should return `{"status":"ok","key_configured":true}`. If
`key_configured` is `false`, the environment variable didn't get set.
