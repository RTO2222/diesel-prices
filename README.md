# Diesel prices

Standard diesel (B7) prices at filling stations inside a set search area, cheapest first. Premium diesel is not included.

A GitHub Action refreshes the list every night. Each day's list is kept in [`prices/history/`](prices/history/), and the latest is in [`prices/latest.csv`](prices/latest.csv).

The prices come from the UK Government Fuel Finder feed (The Motor Fuel Price (Open Data) Regulations 2025), read through [fuel-finder.uk](https://www.fuel-finder.uk/). "Price reported" is when the station last sent its price. Prices change often, so check at the pump.

## Latest prices

<!-- PRICES:START -->
_Last checked: 2026-11-28. 30 stations._

| Station | Postcode | Diesel (p/litre) | Brand | Address | Price reported |
|---|---|---|---|---|---|
| Asda Grosvenor Express Petrol | SK1 3UA | 185.9p | Esso | Wellington New Road, Stockport | 2026-11-26 |
| MFG Morrisons Cheadle Heath | SK3 0RL | 185.9p | Morrisons | Edgeley Road, Edgeley | 2026-11-27 |
| Asda Great Moor Express Petrol | SK2 6HA | 186.9p | Esso | 172-6 Buxton Road, Stockport | 2026-11-26 |
| Hazel Grove Esso Express | SK7 6DT | 186.9p | Esso | 99 Macclesfield Road, Stockport | 2026-11-27 |
| MFG Hall Street | SK1 4DA | 186.9p | Shell | Hall Street, Offerton, Stockport | 2026-11-28 |
| Sainsburys Hazel Grove | SK7 4AW | 186.9p | Sainsburys | London Road, Hazel Grove, Stockport | 2026-11-27 |
| Asda Hazel Grove Express Petrol | SK7 6AF | 187.9p | BP | Buxton Road, Stockport | 2026-11-26 |
| Asda Stockport Express Petrol | SK2 7NR | 187.9p | Asda | 297-309 Buxton Road, Stockport | 2026-11-20 |
| MFG Bramhall | SK7 2BE | 187.9p | Shell | Ack Lane, Bramhall, Stockport | 2026-11-25 |
| MFG Civic Centre | M22 5RG | 187.9p | BP | Rowlands Way, Manchester | 2026-11-27 |
| MFG Red Lion | SK8 2AJ | 187.9p | Esso | 83A Stockport Road, Cheadle | 2026-11-27 |
| The Tower Garage Ltd | SK9 7QB | 187.9p | The Tower Garage Ltd | Highams, Tower Buildings, Wilmslow Road, Alderley Edge, Sk9 7Qb, Alderley Edge | 2026-11-25 |
| Asda Royle Green Express Petrol | M22 4SY | 188.9p | BP | Longley Lane, Manchester | 2026-11-27 |
| BP Offerton green service station | SK2 5AU | 188.9p | BP | Offerton green service station, Marple road, Stockport | 2026-11-27 |
| Rontec St Hildas | M22 4FW | 188.9p | Esso | Palatine Road, Manchester | 2026-11-26 |
| Sainsburys Cheadle | SK8 3BB | 188.9p | Sainsburys | Wilmslow Road, Cheadle | 2026-11-27 |
| Tgc - Styal Road | M22 5WX | 188.9p | Shell | Styal Road, Manchester | 2026-11-27 |
| Airport City SF Connect | WA15 0AF | 189.9p | BP | 2B Sunbank Lane, Manchester | 2026-11-26 |
| Asda Altrincham Road Express Petrol | SK9 5NN | 189.9p | Texaco | Altrincham Road, Wilmslow | 2026-11-26 |
| Asda Wilmslow Express Petrol | SK9 5EH | 189.9p | Asda | Hawthorne Street, Wilmslow | 2026-11-26 |
| Bramhall Esso Express | SK7 1JR | 189.9p | Esso | 37-41 Woodford Rd, Stockport | 2026-11-26 |
| Cheadle Hulme SF Connect | SK8 7JL | 189.9p | BP | Church Road, Cheadle Hulme | 2026-11-25 |
| Wilmslow SF Connect | SK9 1HT | 189.9p | BP | Alderley Road, Wilmslow | 2026-11-26 |
| Shell Dean Row | SK9 2LN | 190.9p | Shell | Adlington Road, Wilmslow | 2026-11-27 |
| Wilmslow Handforth Extra - Petrol Filling Station | SK9 3PA | 190.9p | Tesco | Tesco Stores Ltd, Kiln Croft Lane, Handforth, Wilmslow | 2026-11-24 |
| Macclesfield Hibel Rd Superstore - Petrol Filling Station | SK10 2AB | 192.9p | Tesco | Hibel Rd, Macclesfield | 2026-11-27 |
| Asda Macclesfield Express Petrol | SK11 9JR | 194.9p | Esso | Churchill Way, Macclesfield | 2026-11-25 |
| Shell Broken Cross | SK11 8TU | 195.9p | Shell | 147 147 Broken Cross, Macclesfield | 2026-11-27 |
| Shell Little Waitrose Tytherington | SK10 2JJ | 195.9p | Shell | Manchester Road, Macclesfield | 2026-11-27 |
| Pexall service station Ltd | SK11 9PG | 199.9p | Gulf | Pexall Service Station, Chelford Road,  Henbury, Macclesfield | 2026-11-23 |
<!-- PRICES:END -->

## How it works

- `scripts/fetch_prices.py` asks fuel-finder.uk for the stations around the search area, keeps only those inside it, and writes the CSV files and the table above.
- `.github/workflows/weekly-prices.yml` runs it every day at 23:17 UTC and commits any changes. You can also run it by hand from the Actions tab ("Run workflow").
- The search area is the polygon in [`area.geojson`](area.geojson). Its motorway edges were traced along the M56 and M60 by `scripts/build_area.py`, which you run from the Actions tab ("Build search area") if the corners ever change.
