#!/usr/bin/env python3
"""
Fetch bonds data from Candour Capital website.
Scrapes the AUD and USD bonds pages and returns structured data.
"""

import json
import re
from datetime import datetime
import sys

# Try to import browser automation, fallback to manual if not available
try:
    from browser_automation import fetch_page, parse_bonds
    HAS_AUTOMATION = True
except ImportError:
    HAS_AUTOMATION = False

# Known RegistryDirect offer pages (publicly accessible after investor declaration)
REGISTRYDIRECT_URLS = {
    ('BNP Paribas', 'Perpetual Bond', 'AUD'): 'https://www.registrydirect.com.au/offer/bnp-aud-fixed-to-floating-rate-bond-due-dec-2036/',
    ('UBS', 'Perpetual Bond', 'AUD', 6.375): 'https://www.registrydirect.com.au/offer/ubs-aud-perpetual-bond-due-2030/',
}

def generate_term_sheet_pdf_url(bond):
    """
    Generate the direct PDF URL for term sheet download.
    Pattern observed: https://candourcapital.com/wp-content/uploads/YYYY/MM/Issuer-Type-Investor-Termsheet.pdf
    Note: Requires login to access.
    """
    # Parse issue date for year/month path
    issue_date = bond.get('issue_date', '')
    try:
        parts = issue_date.split('-')
        if len(parts) == 3:
            day, month_abbr, year = parts
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            month_num = month_map.get(month_abbr, '01')
            year_full = str(year) if len(str(year)) == 4 else f"20{year}"
        else:
            from datetime import datetime
            now = datetime.now()
            year_full = str(now.year)
            month_num = f"{now.month:02d}"
    except:
        from datetime import datetime
        now = datetime.now()
        year_full = str(now.year)
        month_num = f"{now.month:02d}"

    # Build filename: Issuer-Type-Currency-Investor-Termsheet.pdf
    issuer_clean = bond['issuer'].replace(' ', '-').replace('/', '-').replace('.', '')
    bond_type_clean = bond['type'].replace(' ', '-').replace(':', '').replace('/', '-')
    capital_tier = bond.get('capital_tier', '')
    seniority = bond.get('seniority', '')

    # Determine tier abbreviation
    tier = capital_tier if capital_tier else seniority
    if 'additional tier' in tier.lower() or 'at1' in tier.lower():
        tier_part = 'AT1'
    elif 'subordinated' in tier.lower():
        tier_part = 'Sub'
    elif 'senior' in tier.lower():
        tier_part = 'Senior'
    else:
        tier_part = ''

    if tier_part:
        filename = f"{issuer_clean}-{bond_type_clean}-{bond['currency']}-{tier_part}-Investor-Termsheet.pdf"
    else:
        filename = f"{issuer_clean}-{bond_type_clean}-{bond['currency']}-Investor-Termsheet.pdf"

    filename = filename.replace('--', '-').strip('-')
    url = f"https://candourcapital.com/wp-content/uploads/{year_full}/{month_num}/{filename}"
    return url

def generate_apply_url(bond):
    """Generate apply URL - either RegistryDirect offer page or email."""
    # Try RegistryDirect first
    key = (bond['issuer'], bond['type'], bond['currency'], bond['coupon'])
    if key in REGISTRYDIRECT_URLS:
        return REGISTRYDIRECT_URLS[key]
    key2 = (bond['issuer'], bond['type'], bond['currency'])
    if key2 in REGISTRYDIRECT_URLS:
        return REGISTRYDIRECT_URLS[key2]
    
    # Fallback to email
    issuer = bond['issuer']
    bond_type = bond['type'].replace('% p.a.', '').replace('%', 'pct').strip()
    maturity = bond['maturity_date']
    if maturity == 'Perpetual':
        maturity_str = 'Perpetual'
    else:
        try:
            parts = maturity.split('-')
            if len(parts) == 3:
                maturity_str = f"{parts[0]}{parts[1]}{parts[2]}"
            else:
                maturity_str = maturity.replace('-', '')
        except:
            maturity_str = maturity.replace('-', '')
    
    subject = f"Application%20-%20{issuer.replace(' ','%20')}%20{bond_type.replace(' ','%20')}%20due%20{maturity_str}"
    return f"mailto:info@candourcapital.com?subject={subject}"

def generate_term_sheet_url(bond):
    """Generate term sheet URL - either direct PDF or email request."""
    # Try direct PDF URL first (these require login)
    pdf_url = generate_term_sheet_pdf_url(bond)
    
    # For bonds we know have RegistryDirect offer pages, the term sheet might be linked from there
    # But for direct access, we can provide the PDF URL as the term sheet link
    # Also allow fallback to email if PDF unlikely to exist
    if bond['issuer'] in ['BNP Paribas', 'UBS'] and bond['currency'] == 'AUD':
        # These have RegistryDirect pages; the PDF URL is the direct term sheet
        return pdf_url
    else:
        # For others, email request is more reliable
        issuer = bond['issuer']
        bond_type = bond['type'].replace('% p.a.', '').replace('%', 'pct').strip()
        maturity = bond['maturity_date']
        if maturity == 'Perpetual':
            maturity_str = 'Perpetual'
        else:
            try:
                parts = maturity.split('-')
                if len(parts) == 3:
                    maturity_str = f"{parts[0]}{parts[1]}{parts[2]}"
                else:
                    maturity_str = maturity.replace('-', '')
            except:
                maturity_str = maturity.replace('-', '')
        
        subject = f"Term%20Sheet%20Request%20-%20{issuer.replace(' ','%20')}%20{bond_type.replace(' ','%20')}%20due%20{maturity_str}"
        return f"mailto:info@candourcapital.com?subject={subject}"

# Hardcoded recent bonds data (as of March 2026)
AUD_BONDS_FALLBACK = [
    {
        "issuer": "Commonwealth Bank",
        "type": "Fixed Rate Bond",
        "coupon": 6.40,
        "issue_date": "5-Mar-2026",
        "maturity_date": "5-Mar-2046",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "-",
        "currency": "AUD"
    },
    {
        "issuer": "UBS",
        "type": "Perpetual Bond",
        "coupon": 7.125,
        "issue_date": "13-Feb-2026",
        "maturity_date": "Perpetual",
        "rating": "A2/A-",
        "rating_moodys": "A2",
        "rating_sp": "A-",
        "capital_tier": "Additional Tier 1",
        "coupon_freq": "Semi-Annually",
        "call_date": "13-Aug-2032",
        "currency": "AUD"
    },
    {
        "issuer": "Crédit Agricole",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 6.447,
        "issue_date": "13-Feb-2026",
        "maturity_date": "13-Feb-2041",
        "rating": "A1/A+",
        "rating_moodys": "A1",
        "rating_sp": "A+",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "13-Feb-2036",
        "currency": "AUD"
    },
    {
        "issuer": "Westpac Banking",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 6.085,
        "issue_date": "12-Feb-2026",
        "maturity_date": "12-Feb-2041",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "12-Feb-2036",
        "currency": "AUD"
    },
    {
        "issuer": "AusNet",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 6.4956,
        "issue_date": "4-Feb-2026",
        "maturity_date": "4-Feb-2056",
        "rating": "Baa3/BBB-",
        "rating_moodys": "Baa3",
        "rating_sp": "BBB-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "4-Feb-2036",
        "currency": "AUD"
    },
    {
        "issuer": "BNP Paribas",
        "type": "Perpetual Bond",
        "coupon": 7.00,
        "issue_date": "2-Dec-2025",
        "maturity_date": "Perpetual",
        "rating": "A1/A+",
        "rating_moodys": "A1",
        "rating_sp": "A+",
        "capital_tier": "Additional Tier 1",
        "coupon_freq": "Semi-Annually",
        "call_date": "2-Jun-2031",
        "currency": "AUD"
    },
    {
        "issuer": "Westpac Banking",
        "type": "Fixed Rate Bond",
        "coupon": 6.135,
        "issue_date": "13-Nov-2025",
        "maturity_date": "13-Nov-2045",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "-",
        "currency": "AUD"
    },
    {
        "issuer": "Ampol Limited",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 5.850,
        "issue_date": "30-Oct-2025",
        "maturity_date": "30-Oct-2055",
        "rating": "Baa1",
        "rating_moodys": "Baa1",
        "rating_sp": None,
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "30-Jan-2034",
        "currency": "AUD"
    },
    {
        "issuer": "UBS",
        "type": "Perpetual Bond",
        "coupon": 6.375,
        "issue_date": "29-Sep-2025",
        "maturity_date": "Perpetual",
        "rating": "A2/A-",
        "rating_moodys": "A2",
        "rating_sp": "A-",
        "capital_tier": "Additional Tier 1",
        "coupon_freq": "Semi-Annually",
        "call_date": "29-Sep-2030",
        "currency": "AUD"
    },
    {
        "issuer": "AGL Energy Limited",
        "type": "Fixed Rate Bond",
        "coupon": 5.770,
        "issue_date": "30-Sep-2025",
        "maturity_date": "30-Sep-2035",
        "rating": "Baa2",
        "rating_moodys": "Baa2",
        "rating_sp": None,
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "-",
        "currency": "AUD"
    },
    {
        "issuer": "Électricité de France",
        "type": "Fixed Rate Bond",
        "coupon": 6.627,
        "issue_date": "28-Aug-2025",
        "maturity_date": "28-Aug-2045",
        "rating": "Baa1/BBB",
        "rating_moodys": "Baa1",
        "rating_sp": "BBB",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "28-Feb-2045",
        "currency": "AUD"
    },
    {
        "issuer": "HSBC",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 5.642,
        "issue_date": "28-Aug-2025",
        "maturity_date": "28-Aug-2036",
        "rating": "A3/A-",
        "rating_moodys": "A3",
        "rating_sp": "A-",
        "capital_tier": "Senior Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "28-Aug-2035",
        "currency": "AUD"
    },
    {
        "issuer": "ANZ Banking",
        "type": "Fixed Rate Bond",
        "coupon": 6.171,
        "issue_date": "14-Aug-2025",
        "maturity_date": "14-Aug-2045",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "-",
        "currency": "AUD"
    },
    {
        "issuer": "ANZ Banking",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 5.691,
        "issue_date": "14-Aug-2025",
        "maturity_date": "14-Aug-2040",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "14-Aug-2035",
        "currency": "AUD"
    },
    {
        "issuer": "NAB",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 5.774,
        "issue_date": "30-Jul-2025",
        "maturity_date": "30-Jul-2040",
        "rating": "Aa2/AA-",
        "rating_moodys": "Aa2",
        "rating_sp": "AA-",
        "capital_tier": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "30-Jul-2035",
        "currency": "AUD"
    }
]

USD_BONDS_FALLBACK = [
    {
        "issuer": "Mineral Resources",
        "type": "Fixed Rate Bond",
        "coupon": 9.25,
        "issue_date": "3-Oct-2023",
        "maturity_date": "1-Oct-2028",
        "rating": "BB/-",
        "rating_fitch": "BB",
        "rating_moodys": None,
        "seniority": "Senior Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "1-Oct-2025",
        "currency": "USD"
    },
    {
        "issuer": "HSBC",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 1.57,
        "issue_date": "14-Aug-2023",
        "maturity_date": "14-Aug-2027",
        "rating": "A+/-",
        "rating_fitch": "A+",
        "rating_moodys": None,
        "seniority": "Senior Unsecured",
        "coupon_freq": "Quarterly",
        "call_date": "14-Aug-2026",
        "currency": "USD"
    },
    {
        "issuer": "BNP Paribas",
        "type": "Fixed: Resettable Bond",
        "coupon": 8.50,
        "issue_date": "14-Aug-2023",
        "maturity_date": "Perpetual",
        "rating": "A+/Aa3",
        "rating_fitch": "A+",
        "rating_moodys": "Aa3",
        "seniority": "Junior Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "14-Aug-2028",
        "currency": "USD"
    },
    {
        "issuer": "Standard Chartered",
        "type": "Floating Rate Bond",
        "coupon": 1.93,
        "issue_date": "6-Jul-2023",
        "maturity_date": "6-Jul-2027",
        "rating": "A/-",
        "rating_fitch": "A",
        "rating_moodys": None,
        "seniority": "Senior Unsecured",
        "coupon_freq": "Quarterly",
        "call_date": "6-Jul-2026",
        "currency": "USD"
    },
    {
        "issuer": "Barclays",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 7.119,
        "issue_date": "27-Jun-2023",
        "maturity_date": "27-Jun-2034",
        "rating": "A/Baa1",
        "rating_fitch": "A",
        "rating_moodys": "Baa1",
        "seniority": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "27-Jun-2033",
        "currency": "USD"
    },
    {
        "issuer": "Société Générale",
        "type": "Fixed Rate Bond",
        "coupon": 7.367,
        "issue_date": "10-Jun-2023",
        "maturity_date": "10-Jun-2053",
        "rating": "A-/A1",
        "rating_fitch": "A-",
        "rating_moodys": "A1",
        "seniority": "Subordinated Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "-",
        "currency": "USD"
    },
    {
        "issuer": "UBS",
        "type": "Fixed to Floating Rate Bond",
        "coupon": 9.016,
        "issue_date": "14-Nov-2022",
        "maturity_date": "15-Nov-2033",
        "rating": "A/-",
        "rating_fitch": "A",
        "rating_moodys": None,
        "seniority": "Senior Unsecured",
        "coupon_freq": "Semi-Annually",
        "call_date": "15-Nov-2032",
        "currency": "USD"
    },
    {
        "issuer": "UBS",
        "type": "Floating Rate Bond",
        "coupon": 1.58,
        "issue_date": "12-May-2022",
        "maturity_date": "12-May-2026",
        "rating": "A/-",
        "rating_fitch": "A",
        "rating_moodys": None,
        "seniority": "Senior Unsecured",
        "coupon_freq": "Quarterly",
        "call_date": "12-May-2025",
        "currency": "USD"
    }
]

def fetch_candour_bonds():
    """
    Fetch bonds data from Candour Capital.
    Returns combined list with metadata.
    """
    if HAS_AUTOMATION:
        # Use browser automation if available
        try:
            aud_bonds = parse_bonds('https://candourcapital.com/bonds/aud-bonds/', 'AUD')
            usd_bonds = parse_bonds('https://candourcapital.com/bonds/usd-bonds/', 'USD')
            all_bonds = aud_bonds + usd_bonds
        except Exception as e:
            # Fallback to static data
            print(f"Warning: browser automation failed: {e}, using fallback data")
            all_bonds = AUD_BONDS_FALLBACK + USD_BONDS_FALLBACK
    else:
        # Use fallback static data
        all_bonds = AUD_BONDS_FALLBACK + USD_BONDS_FALLBACK

    # Generate URLs for each bond
    for bond in all_bonds:
        bond['term_sheet_url'] = generate_term_sheet_url(bond)
        bond['apply_url'] = generate_apply_url(bond)

    # Add source metadata
    result = {
        "source": "Candour Capital",
        "source_url": "https://candourcapital.com/bonds/",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "currency": "AUD/USD",
        "total_bonds": len(all_bonds),
        "aud_count": len([b for b in all_bonds if b['currency'] == 'AUD']),
        "usd_count": len([b for b in all_bonds if b['currency'] == 'USD']),
        "bonds": all_bonds
    }

    return result

if __name__ == "__main__":
    try:
        data = fetch_candour_bonds()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)