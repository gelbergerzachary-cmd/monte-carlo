# 📈 Monte Carlo Stock Simulator

A web app that runs **Geometric Brownian Motion (GBM)** Monte Carlo simulations on real stock data, fetched live via yfinance. Visualizes thousands of possible price paths with confidence bands, rainbow path coloring, and key risk statistics.

---

## Features

- **Live stock data** — fetches 1 year of real price history via yfinance for any ticker
- **GBM simulation** — computes historical drift (μ) and volatility (σ) from log returns, runs vectorised Monte Carlo
- **Up to 5,000 simulations** — adjustable via slider
- **Rainbow price paths** — each path rendered in a unique hue across the full spectrum
- **Confidence bands** — shaded P5/P25/P75/P95 percentile bands with bold median line
- **Vol multiplier** — stress test any ticker by scaling volatility (0.1× to 4×)
- **Scenario presets** — Base / Bull / Bear / Crash with one click
- **Key stats** — current price, median end, 95th/5th percentile, probability of profit, annualised vol
- **Fully responsive** — desktop sidebar layout + mobile slide-in drawer

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Flask · yfinance · NumPy |
| Frontend | Vanilla JS · Chart.js · CSS Grid |
| Fonts | DM Sans · DM Mono (Google Fonts) |
| Deployment | Railway (Gunicorn) |

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/monte-carlo.git
cd monte-carlo

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Start the server
python3 app.py

# 4. Open in browser
open http://localhost:5050
```

---

## How It Works

1. On each simulation run, the backend fetches 1 year of daily closing prices for the requested ticker via `yfinance`
2. Daily log returns are computed: `r = ln(P_t / P_{t-1})`
3. Drift (μ) and volatility (σ) are estimated from the return series
4. σ is scaled by the user's vol multiplier
5. GBM paths are simulated using:

```
S(t+1) = S(t) · exp((μ - ½σ²)dt + σ√dt · Z)
```

where Z ~ N(0,1)

6. All N paths are used to compute percentile bands and statistics
7. Up to 100 sampled paths are returned to the frontend for rendering

---

## Project Structure

```
monte-carlo/
├── app.py            # Flask backend — data fetching + GBM simulation
├── index.html        # Single-file frontend — UI, Chart.js, all styles
├── requirements.txt  # Python dependencies
├── Procfile          # Railway/Render deployment config
└── README.md
```

---

## Deploy to Railway

1. Push to GitHub (see above)
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
3. Select this repo — Railway auto-detects the `Procfile`
4. Go to **Settings → Generate Domain** for a public URL

Auto-deploys on every `git push`.

---

## License

MIT
