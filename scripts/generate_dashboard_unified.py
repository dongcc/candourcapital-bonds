#!/usr/bin/env python3
"""
Generate Candour Capital bonds dashboard with optional currency filter.
Usage: python3 generate_dashboard_unified.py [--currency AUD|USD|ALL]
Default: ALL (shows all bonds)
"""

import json
import subprocess
import os
import sys
import argparse
from datetime import datetime

def fetch_bonds_data():
    """Fetch bonds data from the fetch script."""
    try:
        result = subprocess.run(
            [sys.executable, 'fetch_candour_bonds.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        print(f"Error fetching bonds data: {e}")
        sys.exit(1)

def generate_dashboard(currency='ALL'):
    """Generate dashboard for specified currency."""
    data = fetch_bonds_data()
    
    # Filter bonds by currency if needed
    if currency == 'AUD':
        bonds = [b for b in data['bonds'] if b['currency'] == 'AUD']
        template_file = 'aud_dashboard_template.html'
        output_prefix = 'aud_bonds'
    elif currency == 'USD':
        bonds = [b for b in data['bonds'] if b['currency'] == 'USD']
        template_file = 'usd_dashboard_template.html'
        output_prefix = 'usd_bonds'
    else:
        bonds = data['bonds']
        template_file = 'full_dashboard_template.html'
        output_prefix = 'all_bonds'
    
    if not bonds:
        print(f"No bonds found for currency: {currency}")
        sys.exit(1)
    
    # Calculate summary
    avg_coupon = sum(b['coupon'] for b in bonds) / len(bonds)
    summary = {
        'total_bonds': len(bonds),
        'aud_count': len([b for b in bonds if b['currency'] == 'AUD']),
        'usd_count': len([b for b in bonds if b['currency'] == 'USD']),
        'avg_coupon': round(avg_coupon, 2)
    }
    
    # Prepare dashboard data
    dashboard_data = {
        'source': data['source'],
        'source_url': data['source_url'],
        'last_updated': data['last_updated'],
        'summary': summary,
        'bonds': bonds,
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Load template (look in ../assets/)
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', template_file))
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Inject data
    html_output = template.replace('{{DATA}}', json.dumps(dashboard_data))
    
    # Save output
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'{output_prefix}_{timestamp}.html')
    
    with open(output_file, 'w') as f:
        f.write(html_output)
    
    print(f"✅ Dashboard generated:")
    print(f"   Currency: {currency if currency != 'ALL' else 'All'}")
    print(f"   Bonds: {len(bonds)}")
    print(f"   Avg Coupon: {avg_coupon:.2f}%")
    print(f"   File: {output_file}")
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Candour Capital bonds dashboard')
    parser.add_argument('--currency', choices=['AUD', 'USD', 'ALL'], default='ALL',
                       help='Filter by currency: AUD, USD, or ALL (default)')
    args = parser.parse_args()
    
    generate_dashboard(args.currency)
