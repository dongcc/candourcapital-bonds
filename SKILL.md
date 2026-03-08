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
3. **Extracts term sheet/apply links**: Each bond includes a link to view term sheets or apply (either RegistryDirect offer pages or email contacts)
4. **Optionally downloads PDFs**: Can fetch publicly accessible term sheet PDFs (requires `requests` library)
5. **Generates interactive HTML dashboard** with:
   - Summary statistics cards
   - Coupon rate comparison chart (AUD vs USD)
   - Currency distribution pie chart
   - Coupon rate distribution
   - Maturity timeline visualization
   - Detailed sortable/filterable table with **"Term Sheet / Apply"** links
6. **Includes source attribution** with live link back to Candour Capital

## Usage

Simply ask for Candour Capital bonds analysis:

```
Show me Candour Capital bonds with charts
```

The skill will automatically:
- Scrape the bonds listings
- Create an interactive HTML file
- Open it in your browser
- Provide a screenshot

### Downloading Term Sheets

To download available term sheet PDFs (where publicly accessible):

```bash
cd ~/.openclaw/workspace/skills/candourcapital-bonds/scripts
python3 download_termsheets.py
```

This will:
- Attempt to fetch PDFs from RegistryDirect links
- Skip email links (mailto:) - those require manual email request
- Save files to `output/pdfs/` directory
- Report success/failure for each bond

Note: Many term sheets require authentication on RegistryDirect. Only publicly accessible PDFs will download.

## Output Includes

- **Statistics**: Total bonds, AUD/USD split, average coupon
- **Visualizations**: 4 Chart.js charts (bar, doughnut, pie, line)
- **Table**: Full bond details with filtering tabs (All/AUD/USD)
- **Term Sheet Links**: Direct "View" or "Email" buttons for each bond
- **Source link**: Direct attribution to candourcapital.com/bonds/
- **Ratings**: Color-coded by credit quality (high/medium/low)

## Data Fields

For each bond, the skill captures:
- Issuer name
- Bond type (Fixed Rate, Floating, Perpetual, etc.)
- Coupon rate (% p.a.)
- Issue date
- Maturity date (or "Perpetual")
- Credit rating (Moody's/S&P/Fitch)
- Currency (AUD/USD)
- Call date (if applicable)
- Capital tier / seniority
- Coupon frequency
- **Term sheet URL** (link to view/apply)

## Limitations

- Data is scraped from publicly accessible pages (may require investor declaration click)
- Only includes bonds listed on the website (not exhaustive market)
- No real-time pricing or yield calculations
- Static snapshot (doesn't track intraday changes)
- Intended for wholesale investors only (as per website)
- PDF downloads limited by RegistryDirect authentication requirements

## Files

- `scripts/fetch_candour_bonds.py` - Scrapes and parses bond data with term sheet URLs
- `scripts/generate_dashboard.py` - Creates HTML dashboard with links
- `scripts/download_termsheets.py` - Attempts to download term sheet PDFs
- `assets/dashboard_template.html` - Chart.js template with term sheet column

## Example Output

The dashboard shows recent issuances from:
- **AUD**: Commonwealth Bank, UBS, Westpac, ANZ, NAB, BNP Paribas, HSBC, etc.
- **USD**: Mineral Resources, HSBC, Barclays, Société Générale, UBS, etc.

Each bond has a "📄 View" (or "📧 Email") button linking directly to the term sheet or application page.

All with proper attribution back to Candour Capital.