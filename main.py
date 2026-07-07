"""
Ledger & Verdict — proxy backend
---------------------------------
Sits between the browser frontend and Financial Modeling Prep.
Solves two problems:
  1. FMP doesn't send CORS headers, so browsers refuse the response
     when the frontend calls FMP directly ("Failed to fetch").
  2. Your API key never has to sit in browser JS / a shared file.

Run locally:
    pip install fastapi uvicorn httpx --break-system-packages
    export FMP_API_KEY=your_key_here
    uvicorn main:app --reload --port 8000

Deploy free on Render.com:
    1. Push this folder to a GitHub repo.
    2. render.com -> New -> Web Service -> connect the repo.
    3. Build command:  pip install -r requirements.txt
       Start command:  uvicorn main:app --host 0.0.0.0 --port $PORT
    4. Add an environment variable: FMP_API_KEY = your_key_here
    5. Deploy. You'll get a URL like https://your-app.onrender.com
       Put that URL into the frontend's "Backend URL" field.
"""
import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

FMP_KEY = os.environ.get("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com/stable"

app = FastAPI(title="Ledger & Verdict proxy")

# Allow any origin to call this proxy. Tighten to your deployed
# frontend's exact origin once you have one, for extra safety.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def fmp_get(path: str, params: dict):
    if not FMP_KEY:
        raise HTTPException(500, "Server is missing FMP_API_KEY — set it as an environment variable.")
    params = {**params, "apikey": FMP_KEY}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/{path}", params=params)
    try:
        data = r.json()
    except ValueError:
        raise HTTPException(502, f"FMP returned non-JSON (status {r.status_code}).")
    if isinstance(data, dict) and (data.get("Error Message") or data.get("error") or data.get("message")):
        raise HTTPException(502, data.get("Error Message") or data.get("error") or data.get("message"))
    return data


@app.get("/api/bundle")
async def bundle(symbol: str = Query(..., min_length=1)):
    """One call that returns everything the frontend needs for a ticker."""
    symbol = symbol.upper().strip()
    income, balance, cash, quote, profile = None, None, None, None, None
    errors = {}

    async def safe(name, path, params):
        nonlocal errors
        try:
            return await fmp_get(path, params)
        except HTTPException as e:
            errors[name] = e.detail
            return None

    income = await safe("income", "income-statement", {"symbol": symbol, "period": "annual", "limit": 5})
    balance = await safe("balance", "balance-sheet-statement", {"symbol": symbol, "period": "annual", "limit": 5})
    cash = await safe("cash", "cash-flow-statement", {"symbol": symbol, "period": "annual", "limit": 5})
    quote = await safe("quote", "quote", {"symbol": symbol})
    profile = await safe("profile", "profile", {"symbol": symbol})

    hist, spy = None, None
    try:
        from datetime import date, timedelta
        frm = (date.today() - timedelta(days=730)).isoformat()
        hist = await fmp_get("historical-price-eod/full", {"symbol": symbol, "from": frm})
        spy = await fmp_get("historical-price-eod/full", {"symbol": "SPY", "from": frm})
    except HTTPException:
        pass  # price history is best-effort; frontend falls back to published beta

    if not income and not balance and not cash and not quote:
        raise HTTPException(502, f"No data returned for {symbol}. Errors: {errors}")

    return {
        "income": income, "balance": balance, "cash": cash,
        "quote": quote, "profile": profile, "hist": hist, "spy": spy,
        "errors": errors or None,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "key_configured": bool(FMP_KEY)}
