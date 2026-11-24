# Diesel prices

Standard diesel (B7) prices at filling stations within 5 miles of a fixed point, cheapest first. Premium diesel is not included.

A GitHub Action refreshes the list every Sunday night. Each week's list is kept in [`prices/history/`](prices/history/), and the latest is in [`prices/latest.csv`](prices/latest.csv).

The prices come from the UK Government Fuel Finder feed (The Motor Fuel Price (Open Data) Regulations 2025), read through [fuel-finder.uk](https://www.fuel-finder.uk/). "Price reported" is when the station last sent its price. Prices change often, so check at the pump.

## Latest prices

<!-- PRICES:START -->
_Last checked: 2026-11-24. 16 stations._

| Station | Postcode | Diesel (p/litre) | Brand | Address | Price reported |
|---|---|---|---|---|---|
| Asda Stockport Express Petrol | SK2 7NR | 187.9p | Asda | 297-309 Buxton Road, Stockport | 2026-11-20 |
| Sainsburys Hazel Grove | SK7 4AW | 187.9p | Sainsburys | London Road, Hazel Grove, Stockport | 2026-11-22 |
| Hazel Grove Esso Express | SK7 6DT | 188.9p | Esso | 99 Macclesfield Road, Stockport | 2026-11-23 |
| MFG Bramhall | SK7 2BE | 189.9p | Shell | Ack Lane, Bramhall, Stockport | 2026-11-23 |
| Asda Great Moor Express Petrol | SK2 6HA | 191.9p | Esso | 172-6 Buxton Road, Stockport | 2026-11-23 |
| Asda Hazel Grove Express Petrol | SK7 6AF | 191.9p | BP | Buxton Road, Stockport | 2026-11-20 |
| Asda Marple Express Petrol | SK6 6DQ | 191.9p | Texaco | 151 Stockport Road, Marple, Stockport | 2026-11-23 |
| Bramhall Esso Express | SK7 1JR | 192.9p | Esso | 37-41 Woodford Rd, Stockport | 2026-11-23 |
| Cheadle Hulme SF Connect | SK8 7JL | 192.9p | BP | Church Road, Cheadle Hulme | 2026-11-21 |
| High Peak Whaley Bridge Superstore - Petrol Filling Station | SK23 7PD | 192.9p | Tesco | Tesco, Bridgemont, Whaley Bridge, High Peak | 2026-11-13 |
| Rontec Disley | SK12 2HG | 192.9p | Esso | Buxton Road, Stockport | 2026-11-17 |
| Wilmslow Handforth Extra - Petrol Filling Station | SK9 3PA | 192.9p | Tesco | Tesco Stores Ltd, Kiln Croft Lane, Handforth, Wilmslow | 2026-11-13 |
| Shell Dean Row | SK9 2LN | 193.9p | Shell | Adlington Road, Wilmslow | 2026-11-20 |
| G R Yeates Limited | SK6 6AE | 194.9p | Shell | 54 Stockport Rd, Marple | 2026-11-22 |
| Macclesfield Hibel Rd Superstore - Petrol Filling Station | SK10 2AB | 195.9p | Tesco | Hibel Rd, Macclesfield | 2026-11-23 |
| Shell Little Waitrose Tytherington | SK10 2JJ | 198.9p | Shell | Manchester Road, Macclesfield | 2026-11-17 |
<!-- PRICES:END -->

## How it works

- `scripts/fetch_prices.py` asks fuel-finder.uk for the stations within 5 miles of the search point and writes the CSV files and the table above.
- `.github/workflows/weekly-prices.yml` runs it on Sundays at 23:17 UTC and commits any changes. You can also run it by hand from the Actions tab ("Run workflow").
- The search point is kept in two repository secrets, `SEARCH_LAT` and `SEARCH_LNG`, so it isn't in the code.
