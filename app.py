from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

EIA_API_KEY = "YiOiJvFtPMciuUXmwIjotKCIPGNaUjGbKo2sgIpd"  # our actual key

def fetch_oil_price():
    url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={EIA_API_KEY}&frequency=daily&data[0]=value&facets[series][]=RBRTE&sort[0][column]=period&sort[0][direction]=desc&length=1"
    response = requests.get(url)
    data = response.json()
    return float(data['response']['data'][0]['value'])

@app.route('/api/dashboard-data')
def get_dashboard_data():
    oil_price = fetch_oil_price()
    oil_shock = (oil_price - 75.0) / 10 * 0.0025
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'oil_price': oil_price,
        'scenario1': {
            'cpi': 2.0, 'bbr': 4.5, 'savings': 4.0, 'mortgage': 6.0, 'gilt': 6.0
        },
        'scenario2': {
            'cpi': 0.03, 'bbr': 0.0375, 
            'savings': 0.0331, 'mortgage': 0.049, 
            'gilt': 0.043732, 'gbpusd': 1.352
        },
        'scenario3': {
            'cpi': 0.03 + oil_shock,
            'bbr': 0.03 + oil_shock + 0.025,
            'savings': 0.03 + oil_shock + 0.02,
            'mortgage': 0.03 + oil_shock + 0.04,
            'gilt': 0.03 + oil_shock + 0.04
        }
    })

if __name__ == '__main__':
    app.run(port=5000)
