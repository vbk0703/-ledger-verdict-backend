# Ledger & Verdict — Automated Equity Research

A full-stack tool that turns a single stock ticker into a complete
research memo: financial statements, a 3-scenario DCF valuation,
CAPM-based discount rate with regressed beta, and a rules-based
Buy / Hold / Sell verdict — the way a junior equity analyst would
build a first-pass model.

**Live demo:** [add your frontend hosting link here once deployed, or note "open equity-research-mvp.html locally"]

## What it does

- Pulls income statement, balance sheet, cash flow, and live quote data
- Runs a 5-year DCF with Bear / Base / Bull growth scenarios
- Calculates beta by regressing 2 years of daily returns against SPY
  (falls back to published beta if price history is unavailable)
- Builds the discount rate via CAPM (risk-free rate + β × equity risk premium)
- Screens financial health: Altman Z-score, debt/equity, current ratio,
  ROE, margins, FCF yield
- Scores all of the above into a single Buy / Hold / Sell call, with
  every point of the reasoning shown — no black box

## Architecture

- **Frontend:** single-file HTML/CSS/JS (no framework, no build step)
- **Backend:** FastAPI proxy (`main.py`) — hides the API key server-side
  and adds CORS so the browser can call it
- **Data source:** Financial Modeling Prep

## Tech stack

Python · FastAPI · httpx · vanilla JavaScript · Financial Modeling Prep API

## Run it yourself

See setup instructions in this repo, or deploy the backend free on
Render.com and point the frontend's "Backend URL" field at your deployment.

## Disclaimer

Educational project, not investment advice. DCF outputs are highly
sensitive to growth, discount rate, and terminal value assumptions.
