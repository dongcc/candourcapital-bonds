#!/usr/bin/env python3
"""
Generate Candour Capital bonds analysis dashboard.
"""

import json
import subprocess
import os
import sys
from datetime import datetime

def generate_dashboard():
    # Step 1: Fetch bonds data
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
        sys.exit(1)

    if 'error' in data:
        print(json.dumps(data))
        sys.exit(1)

    bonds = data['bonds']

    # Step 2: Calculate statistics
    total_bonds = len(bonds)
    aud_bonds = [b for b in bonds if b['currency'] == 'AUD']
    usd_bonds = [b for b in bonds if b['currency'] == 'USD']
    avg_coupon = sum(b['coupon'] for b in bonds) / total_bonds if total_bonds > 0 else 0

    # Step 3: Prepare data for template
    dashboard_data = {
        'source': data['source'],
        'source_url': data['source_url'],
        'last_updated': data['last_updated'],
        'summary': {
            'total_bonds': total_bonds,
            'aud_count': len(aud_bonds),
            'usd_count': len(usd_bonds),
            'avg_coupon': round(avg_coupon, 2)
        },
        'bonds': bonds,
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Step 4: Load template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'dashboard_template.html')
    template_path = os.path.abspath(template_path)
    with open(template_path, 'r') as f:
        template = f.read()

    # Inject data
    html_output = template.replace('{{DATA}}', json.dumps(dashboard_data))

    # Step 5: Save output
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'candour_bonds_{timestamp}.html')

    with open(output_file, 'w') as f:
        f.write(html_output)

    # Return success with file path
    result = {
        'success': True,
        'html_file': output_file,
        'message': f'Bonds dashboard generated: {output_file}',
        'stats': {
            'total_bonds': total_bonds,
            'aud_bonds': len(aud_bonds),
            'usd_bonds': len(usd_bonds),
            'avg_coupon': round(avg_coupon, 2)
        }
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    generate_dashboard()
