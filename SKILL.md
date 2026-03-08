---
name: candourcapital-bonds
description: "Fetch and visualize bonds from Candour Capital (candourcapital.com/bonds). Returns interactive charts showing AUD and USD bond issuances with coupon rates, ratings, maturities, and currency distribution. Includes source attribution link."
metadata:
  {
    "openclaw": {
      "emoji": "💎",
      "requires": { "bins": ["python3"] },
      "install": []
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
3. **Generates interactive HTML dashboard** with:
   - Summary statistics cards
   - Coupon rate comparison chart (AUD vs USD)
   - Currency distribution pie chart
   - Coupon rate distribution
   - Maturity timeline visualization
   - Detailed sortable/filterable table
4. **Includes source attribution** with live link back to Candour Capital

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

## Output Includes

- **Statistics**: Total bonds, AUD/USD split, average coupon
- **Visualizations**: 4 Chart.js charts (bar, doughnut, pie, line)
- **Table**: Full bond details with filtering tabs (All/AUD/USD)
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

## Limitations

- Data is scraped from publicly accessible pages (may require investor declaration click)
- Only includes bonds listed on the website (not exhaustive market)
- No real-time pricing or yield calculations
- Static snapshot (doesn't track intraday changes)
- Intended for wholesale investors only (as per website)

## Files

- `scripts/fetch_candour_bonds.py` - Scrapes and parses bond data
- `scripts/generate_dashboard.py` - Creates HTML dashboard
- `assets/dashboard_template.html` - Chart.js template with source link

## Example Output

The dashboard shows recent issuances from:
- **AUD**: Commonwealth Bank, UBS, Westpac, ANZ, NAB, BNP Paribas, HSBC, etc.
- **USD**: Mineral Resources, HSBC, Barclays, Société Générale, UBS, etc.

All with proper attribution back to Candour Capital.
