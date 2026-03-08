#!/usr/bin/env python3
"""
Download term sheet PDFs for Candour Capital bonds.
Attempts to fetch PDFs from the term_sheet_urls.
"""

import json
import os
import re
import sys
import requests
from urllib.parse import quote
from datetime import datetime

def sanitize_filename(name):
    """Remove invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).replace(' ', '_')

def download_termsheets(bonds_data, output_dir=None):
    """
    Download term sheets for bonds that have publicly accessible URLs.
    Skips mailto: links. Returns download status for each.
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'output', 'pdfs')
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for bond in bonds_data:
        url = bond.get('term_sheet_url') or bond.get('apply_url')
        if not url or url.startswith('mailto:'):
            results.append({
                'issuer': bond['issuer'],
                'coupon': bond['coupon'],
                'currency': bond['currency'],
                'status': 'skipped',
                'reason': 'mailto link (requires email request)',
                'url': url
            })
            continue
        
        try:
            # Try to download
            response = session.get(url, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                # Determine filename
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' in content_type or url.lower().endswith('.pdf'):
                    ext = '.pdf'
                elif 'html' in content_type or url.lower().endswith('.html'):
                    ext = '.html'
                else:
                    ext = '.pdf'  # assume PDF
                
                filename = f"{sanitize_filename(bond['issuer'])}_{bond['coupon']}pct_{bond['currency']}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                results.append({
                    'issuer': bond['issuer'],
                    'coupon': bond['coupon'],
                    'currency': bond['currency'],
                    'status': 'downloaded',
                    'filepath': filepath,
                    'size_bytes': len(response.content),
                    'url': url
                })
            else:
                results.append({
                    'issuer': bond['issuer'],
                    'coupon': bond['coupon'],
                    'currency': bond['currency'],
                    'status': 'failed',
                    'reason': f'HTTP {response.status_code}',
                    'url': url
                })
        except Exception as e:
            results.append({
                'issuer': bond['issuer'],
                'coupon': bond['coupon'],
                'currency': bond['currency'],
                'status': 'error',
                'reason': str(e),
                'url': url
            })
    
    return results

def main():
    # Load bonds data
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
    
    # Download term sheets
    download_results = download_termsheets(bonds)
    
    # Summary
    downloaded = [r for r in download_results if r['status'] == 'downloaded']
    skipped = [r for r in download_results if r['status'] == 'skipped']
    failed = [r for r in download_results if r['status'] in ['failed', 'error']]
    
    summary = {
        'total_bonds': len(bonds),
        'downloaded': len(downloaded),
        'skipped': len(skipped),
        'failed': len(failed),
        'results': download_results,
        'output_directory': os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', 'pdfs')),
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    import subprocess
    main()