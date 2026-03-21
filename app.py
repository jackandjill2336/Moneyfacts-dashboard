from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)
CORS(app)

EIA_API_KEY = os.environ.get('EIA_API_KEY', 'YiOiJvFtPMciuUXmwIjotKCIPGNaUjGbKo2sgIpd')

# Global cache
cached_data = None
cache_timestamp = None
CACHE_DURATION = 60  # seconds

def fetch_data_background():
    """Background thread to fetch data"""
    global cached_data, cache_timestamp
    
    while True:
        try:
            # 1. Oil
            url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={EIA_API_KEY}&frequency=daily&data[0]=value&facets[series][]=RBRTE&sort[0][column]=period&sort[0][direction]=desc&length=1"
            oil_data = requests.get(url, timeout=5).json()
            oil_price = float(oil_data['response']['data'][0]['value'])
            
            # 2. Gas
            url = f"https://api.eia.gov/v2/natural-gas/pri/fut/data/?api_key={EIA_API_KEY}&frequency=daily&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&length=1"
            gas_data = requests.get(url, timeout=5).json()
            gas_price = float(gas_data['response']['data'][0]['value'])
            
            # Calculate impacts
            oil_impact = ((oil_price - 75.0) / 10) * 0.25
            gas_impact = ((gas_price - 2.50) / 2.50) * 0.20
            external_shock = oil_impact + gas_impact
            
            # Internal factors
            productivity_impact = 0.29
            nics_impact = 0.50
            nlw_impact = 0.20
            brexit_impact = 0.50
            internal_shock = productivity_impact + nics_impact + nlw_impact + brexit_impact
            
            total_impact = external_shock + internal_shock
            
            # Current baseline
            current_cpi = 0.0300
            current_bbr = 0.0375
            current_savings = 0.0331
            current_mortgage = 0.0490
            current_gilt = 0.0437
            current_gbpusd = 1.3520
            
            # Scenario 3
            adjusted_cpi = current_cpi + (total_impact / 100)
            recommended_bbr = adjusted_cpi + 0.025
            recommended_savings = recommended_bbr - 0.005
            recommended_mortgage = adjusted_cpi + 0.040
            recommended_gilt = recommended_bbr + 0.015
            
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'oil_price': oil_price,
                'gas_price': gas_price,
                'oil_impact': oil_impact,
                'gas_impact': gas_impact,
                'external_shock': external_shock,
                'productivity_impact': productivity_impact,
                'nics_impact': nics_impact,
                'nlw_impact': nlw_impact,
                'brexit_impact': brexit_impact,
                'internal_shock': internal_shock,
                'total_impact': total_impact,
                'scenario1': {
                    'cpi': 0.02,
                    'bbr': 0.045,
                    'savings': 0.04,
                    'mortgage': 0.06,
                    'gilt': 0.06
                },
                'scenario2': {
                    'cpi': current_cpi,
                    'bbr': current_bbr,
                    'savings': current_savings,
                    'mortgage': current_mortgage,
                    'gilt': current_gilt,
                    'gbpusd': current_gbpusd
                },
                'scenario3': {
                    'cpi': adjusted_cpi,
                    'bbr': recommended_bbr,
                    'savings': recommended_savings,
                    'mortgage': recommended_mortgage,
                    'gilt': recommended_gilt
                },
                'policy_gap': current_bbr - recommended_bbr,
                'unemployment': 0.052
            }
            cache_timestamp = datetime.now()
            print(f"Data refreshed at {cache_timestamp}")
            
        except Exception as e:
            print(f"Error fetching data: {e}")
        
        time.sleep(CACHE_DURATION)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    if cached_data:
        return jsonify(cached_data)
    else:
        return jsonify({'error': 'Data loading...'}), 503

if __name__ == '__main__':
    # Start background data fetcher
    thread = threading.Thread(target=fetch_data_background, daemon=True)
    thread.start()
    
    # Give it 2 seconds to fetch initial data
    time.sleep(2)
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
