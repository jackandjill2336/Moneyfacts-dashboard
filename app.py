from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

EIA_API_KEY = "YiOiJvFtPMciuUXmwIjotKCIPGNaUjGbKo2sgIpd"

@app.route('/api/dashboard-data')
def get_dashboard_data():
    try:
        # 1. Oil
        url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={EIA_API_KEY}&frequency=daily&data[0]=value&facets[series][]=RBRTE&sort[0][column]=period&sort[0][direction]=desc&length=1"
        oil_data = requests.get(url).json()
        oil_price = float(oil_data['response']['data'][0]['value'])
        
        # 2. Gas
        url = f"https://api.eia.gov/v2/natural-gas/pri/fut/data/?api_key={EIA_API_KEY}&frequency=daily&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&length=1"
        gas_data = requests.get(url).json()
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
        
        # Total impact
        total_impact = external_shock + internal_shock
        
        # Current baseline (from Darren's data)
        current_cpi = 0.0300
        current_bbr = 0.0375
        current_savings = 0.0331
        current_mortgage = 0.0490
        current_gilt = 0.0437
        current_gbpusd = 1.3520
        
        # Scenario 3: Adjusted for all factors
        adjusted_cpi = current_cpi + (total_impact / 100)
        recommended_bbr = adjusted_cpi + 0.025
        recommended_savings = recommended_bbr - 0.005
        recommended_mortgage = adjusted_cpi + 0.040
        recommended_gilt = recommended_bbr + 0.015
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            
            # External factors
            'oil_price': oil_price,
            'gas_price': gas_price,
            'oil_impact': oil_impact,
            'gas_impact': gas_impact,
            'external_shock': external_shock,
            
            # Internal factors
            'productivity_impact': productivity_impact,
            'nics_impact': nics_impact,
            'nlw_impact': nlw_impact,
            'brexit_impact': brexit_impact,
            'internal_shock': internal_shock,
            
            # Total
            'total_impact': total_impact,
            
            # Scenario 1: Ideal
            'scenario1': {
                'cpi': 0.02,
                'bbr': 0.045,
                'savings': 0.04,
                'mortgage': 0.06,
                'gilt': 0.06
            },
            
            # Scenario 2: Current
            'scenario2': {
                'cpi': current_cpi,
                'bbr': current_bbr,
                'savings': current_savings,
                'mortgage': current_mortgage,
                'gilt': current_gilt,
                'gbpusd': current_gbpusd
            },
            
            # Scenario 3: Adjusted
            'scenario3': {
                'cpi': adjusted_cpi,
                'bbr': recommended_bbr,
                'savings': recommended_savings,
                'mortgage': recommended_mortgage,
                'gilt': recommended_gilt
            },
            
            # Policy gap
            'policy_gap': current_bbr - recommended_bbr,
            'unemployment': 0.052        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
