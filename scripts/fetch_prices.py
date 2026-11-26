#!/usr/bin/env python3
"""Fetch standard diesel (B7) prices for filling stations within a radius of a
search point and write them to prices/latest.csv, a dated copy in
prices/history/, and the table in README.md.

The search point is read from the SEARCH_LAT and SEARCH_LNG environment
variables (stored as GitHub Actions secrets) so it never appears in the repo.
Prices come from the UK Government Fuel Finder feed, via fuel-finder.uk.
"""

import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RADIUS_MILES = float(os.environ.get("RADIUS_MILES", "10"))
API = "https://www.fuel-finder.uk/api/stations/"
COLUMNS = ["Station", "Postcode", "Diesel (p/litre)", "Brand", "Address", "Price reported"]


def fetch(lat: str, lng: str) -> list[dict]:
    query = urllib.parse.urlencode({
        "lat": lat,
        "lng": lng,
        "fuel_type": "diesel",
        "radius": RADIUS_MILES,
        "sort": "price",
        "pricing_mode": "pump",
    })
    req = urllib.request.Request(
        f"{API}?{query}",
        headers={
            "User-Agent": "Mozilla/5.0 (weekly diesel price log; github.com/RTO2222)",
            "Accept": "application/json",
            "Referer": "https://www.fuel-finder.uk/",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    stations = data.get("stations", [])
    print(f"API returned {len(stations)} stations; stats: {json.dumps(data.get('stats'))[:500]}")
    return stations


def tidy(text: str) -> str:
    """Station names in the feed are often in capitals; make them readable."""
    if not text:
        return ""
    if text.isupper():
        text = text.title()
        # keep common short codes in capitals
        text = re.sub(r"\b(Mfg|Bp|Sf|Gr)\b", lambda m: m.group(1).upper(), text)
    return text.strip()


def to_rows(stations: list[dict]) -> list[list]:
    rows = []
    for s in stations:
        if s.get("temporary_closure") or s.get("permanent_closure"):
            continue
        price = s.get("price_diesel")
        if price is None:
            continue
        if s.get("distance") is not None and float(s["distance"]) > RADIUS_MILES:
            continue
        reported = (s.get("price_last_updated_iso") or "")[:10]
        rows.append([
            tidy(s.get("name", "")),
            s.get("postcode", ""),
            f"{float(price):.1f}",
            s.get("brand", ""),
            tidy(s.get("address", "")),
            reported,
        ])
    rows.sort(key=lambda r: (float(r[2]), r[0]))
    return rows


def write_csv(path: Path, rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        w.writerows(rows)


def update_readme(rows: list[list], checked: str) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    lines = [
        f"_Last checked: {checked}. {len(rows)} stations._",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "|" + "|".join(["---"] * len(COLUMNS)) + "|",
    ]
    for r in rows:
        cells = list(r)
        cells[2] = f"{cells[2]}p"
        lines.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    table = "\n".join(lines)
    new = re.sub(
        r"<!-- PRICES:START -->.*<!-- PRICES:END -->",
        f"<!-- PRICES:START -->\n{table}\n<!-- PRICES:END -->",
        text,
        flags=re.S,
    )
    readme.write_text(new, encoding="utf-8")


def main() -> int:
    lat, lng = os.environ.get("SEARCH_LAT"), os.environ.get("SEARCH_LNG")
    if not lat or not lng:
        print("SEARCH_LAT and SEARCH_LNG must be set (repository secrets).", file=sys.stderr)
        return 1
    stations = fetch(lat, lng)
    rows = to_rows(stations)
    if not rows:
        print("No stations with diesel prices returned; leaving files unchanged.", file=sys.stderr)
        return 1
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    write_csv(ROOT / "prices" / "latest.csv", rows)
    write_csv(ROOT / "prices" / "history" / f"{today}.csv", rows)
    update_readme(rows, today)
    print(f"Wrote {len(rows)} stations for {today}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
