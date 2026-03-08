#!/usr/bin/env python3
"""
Generate USD-only Candour Capital bonds dashboard.
"""

import json
import subprocess
import os
import sys
from datetime import datetime

def generate_usd_dashboard():
    # Fetch all bonds data
    try:
        result = subprocess.run(
            [sys.executable, 'fetch_candour_bonds.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        data = json.loads(result.stdout)
    except Exception as e:
        print(json.dumps({'error': f'Failed to fetch bonds data: {str(e)}'}))
        return

    if 'error' in data:
        print(json.dumps(data))
        return

    # Filter to USD only
    usd_bonds = [b for b in data['bonds'] if b['currency'] == 'USD']
    if not usd_bonds:
        print("No USD bonds found")
        return

    avg_coupon = sum(b['coupon'] for b in usd_bonds) / len(usd_bonds)

    # Prepare dashboard data
    dashboard_data = {
        'source': data['source'],
        'source_url': data['source_url'],
        'last_updated': data['last_updated'],
        'summary': {
            'total_bonds': len(usd_bonds),
            'aud_count': 0,
            'usd_count': len(usd_bonds),
            'avg_coupon': round(avg_coupon, 2)
        },
        'bonds': usd_bonds,
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'usd_dashboard_template.html')
    template_path = os.path.abspath(template_path)
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholder with JSON data
    html_output = template.replace('{{DATA}}', json.dumps(dashboard_data))

    # Save output
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'usd_bonds_{timestamp}.html')

    with open(output_file, 'w') as f:
        f.write(html_output)

    print(f"✅ USD Bonds dashboard generated:")
    print(f"   File: {output_file}")
    print(f"   Bonds: {len(usd_bonds)}")
    print(f"   Avg Coupon: {avg_coupon:.2f}%")
    print(f"\nOpen in browser: file://{output_file}")

if __name__ == "__main__":
    generate_usd_dashboard()
