---
name: candourcapital-bonds
description: "Fetch and visualize bonds from Candour Capital (candourcapital.com/bonds). Returns interactive charts showing AUD and USD bond issuances with coupon rates, ratings, maturities, and currency distribution. Includes source attribution link and term sheet access."
metadata:
  {
    "openclaw": {
      "emoji": "💎",
      "requires": { "bins": ["python3"] },
      "install": [
        {
          "id": "pip",
          "kind": "pip",
          "packages": ["requests"],
          "label": "Install requests library for PDF downloads"
        }
      ]
    }
  }
---

# Candour Capital Bonds Skill

## Overview

This skill queries Candour Capital's bonds listings to retrieve current AUD and USD bond offerings, then generates an interactive visual dashboard with charts and tables. It's designed for financial professionals and wholesale investors researching fixed income opportunities.

**Trigger phrases:**
- "Show Candour Capital bonds"
- "Get bonds list from Candour Capital"
- "Visualize Candour Capital bond offerings"
- "Candour Capital AUD and USD bonds with charts"
- "Analyze Candour Capital bonds"

## What It Does

1. **Fetches data** from `https://candourcapital.com/bonds/` (both AUD and USD bond pages)
2. **Parses bond details**: issuer, type, coupon rate, issue/maturity dates, ratings, currency
3. **Generates term sheet/apply links**: 
   - RegistryDirect offer pages (where available)
   - Email links with pre-filled subjects for term sheet requests or applications
4. **Creates interactive HTML dashboards** with:
   - Summary statistics cards
   - Coupon rate comparison chart (AUD vs USD)
   - Currency distribution pie chart
   - Coupon rate distribution
   - Maturity timeline visualization
   - Detailed sortable/filterable table with **separate Term Sheet and Apply** links
5. **Includes source attribution** with live link back to Candour Capital

## Usage

### All Bonds Dashboard (Default)
```
Show me Candour Capital bonds with charts
```
Generates a dashboard with all 23 bonds (15 AUD + 8 USD) with filtering tabs.

### Currency-Specific Dashboards
```
Show me Candour Capital AUD bonds with charts
Show me Candour Capital USD bonds with charts
```

### Command-Line Usage
```bash
cd ~/.openclaw/workspace/skills/candourcapital-bonds/scripts
python3 generate_dashboard_unified.py --currency ALL   # All bonds (default)
python3 generate_dashboard_unified.py --currency AUD   # AUD only (15 bonds)
python3 generate_dashboard_unified.py --currency USD   # USD only (8 bonds)
```

Each command generates an HTML file in `output/` and can be opened in a browser.

## Output Includes

- **Statistics**: Total bonds, AUD/USD split, average coupon
- **Visualizations**: 4 Chart.js charts
  - Coupon rates bar chart (by issuer, colored by currency)
  - Currency distribution doughnut chart
  - Coupon distribution pie chart (by range)
  - Maturity timeline line chart
- **Detailed table** with columns:
  - Issuer, Type, Coupon, Issue Date, Maturity, Rating, Currency
  - **Term Sheet** button (📄 PDF or 📧 Email)
  - **Apply** button (🖊️ Apply or 📧 Email)
- **Filtering tabs**: All / AUD Only / USD Only
- **Source attribution** with live link

## Term Sheet Access

- **Direct PDF**: For select bonds with RegistryDirect offer pages (e.g., UBS 6.375% AUD, BNP Paribas AUD). Clicking downloads the term sheet (may require login).
- **Email Request**: For most bonds, clicking opens email client with a pre-filled, properly formatted subject line to info@candourcapital.com.
- **Apply**: Links to RegistryDirect application pages where available, otherwise email.

## Data Fields

Each bond includes:
- Issuer, Type, Coupon (% p.a.), Issue Date, Maturity Date, Rating
- Currency (AUD/USD), Call Date, Capital Tier/Seniority, Coupon Frequency
- `term_sheet_url` and `apply_url`

## Limitations

- Data is scraped from publicly accessible pages (may require investor declaration)
- Only includes bonds listed on the website
- No real-time pricing or yield calculations
- Static snapshot
- Intended for wholesale investors only

## Files

- `scripts/fetch_candour_bonds.py` - Fetches and parses bond data
- `scripts/generate_dashboard_unified.py` - Main dashboard generator (supports ALL/AUD/USD)
- `scripts/generate_aud_dashboard.py` - AUD-only generator (legacy)
- `scripts/generate_usd_dashboard.py` - USD-only generator (legacy)
- `assets/full_dashboard_template.html` - Template for all bonds
- `assets/aud_dashboard_template.html` - Template for AUD only
- `assets/usd_dashboard_template.html` - Template for USD only

## Example Output

The dashboard displays recent issuances from:
- **AUD**: Commonwealth Bank, UBS, Westpac, ANZ, NAB, BNP Paribas, HSBC, Crédit Agricole, Ampol, AGL, AusNet, Électricité de France, etc.
- **USD**: Mineral Resources, HSBC, Barclays, BNP Paribas, Standard Chartered, Société Générale, UBS.

All with proper attribution back to Candour Capital.