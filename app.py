from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import numpy as np
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    ticker = data.get('ticker', 'AAPL').upper().strip()
    days = max(1, min(int(data.get('days', 252)), 1260))
    num_paths = max(10, min(int(data.get("num_paths", 200)), 5000))
    vol_override = float(data.get('vol_override', 1.0))

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')

        if hist.empty or len(hist) < 20:
            return jsonify({'error': f'No data found for "{ticker}". Check the ticker symbol.'}), 400

        closes = hist['Close'].values
        current_price = float(closes[-1])

        log_returns = np.diff(np.log(closes))
        mu = float(np.mean(log_returns))
        sigma = float(np.std(log_returns)) * vol_override

        dt = 1
        rng = np.random.default_rng()
        Z = rng.standard_normal((num_paths, days))
        daily = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
        log_paths = np.concatenate([
            np.zeros((num_paths, 1)),
            np.cumsum(daily, axis=1)
        ], axis=1)
        paths_array = current_price * np.exp(log_paths)

        final_prices = paths_array[:, -1]

        p5  = np.percentile(paths_array, 5,  axis=0).tolist()
        p25 = np.percentile(paths_array, 25, axis=0).tolist()
        p50 = np.percentile(paths_array, 50, axis=0).tolist()
        p75 = np.percentile(paths_array, 75, axis=0).tolist()
        p95 = np.percentile(paths_array, 95, axis=0).tolist()

        n_sample = min(100, num_paths)
        idx = rng.choice(num_paths, n_sample, replace=False)
        sampled_paths = paths_array[idx].tolist()

        return jsonify({
            'ticker': ticker,
            'current_price': round(current_price, 4),
            'days': days,
            'num_paths': num_paths,
            'annual_vol': round(sigma * np.sqrt(252) * 100, 2),
            'daily_drift': round(mu * 100, 4),
            'paths': sampled_paths,
            'bands': {'p5': p5, 'p25': p25, 'p50': p50, 'p75': p75, 'p95': p95},
            'stats': {
                'median_end':  round(float(np.median(final_prices)), 2),
                'mean_end':    round(float(np.mean(final_prices)), 2),
                'p5_end':      round(float(np.percentile(final_prices, 5)), 2),
                'p95_end':     round(float(np.percentile(final_prices, 95)), 2),
                'prob_profit': round(float(np.mean(final_prices > current_price)) * 100, 1),
                'max_gain':    round(float((np.max(final_prices) - current_price) / current_price * 100), 1),
                'max_loss':    round(float((np.min(final_prices) - current_price) / current_price * 100), 1),
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
