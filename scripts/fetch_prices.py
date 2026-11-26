#!/usr/bin/env python3
"""Fetch standard diesel (B7) prices for filling stations within a radius of a
search point and write them to prices/latest.csv, a dated copy in
prices/history/, and the table in README.md.

Only stations inside the search area in area.geojson are kept (see
scripts/build_area.py). Prices come from the UK Government Fuel Finder feed,
via fuel-finder.uk.
"""

import csv
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://www.fuel-finder.uk/api/stations/"
COLUMNS = ["Station", "Postcode", "Diesel (p/litre)", "Brand", "Address", "Price reported", "Lat", "Lng"]
README_COLUMNS = 6  # the README table leaves out Lat and Lng


def load_area() -> list[list[float]]:
    geo = json.loads((ROOT / "area.geojson").read_text(encoding="utf-8"))
    return geo["features"][0]["geometry"]["coordinates"][0]  # [lng, lat]


def miles_between(lat1, lng1, lat2, lng2) -> float:
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def search_circle(ring):
    """A circle that covers the whole area, for the API query."""
    lngs, lats = [p[0] for p in ring], [p[1] for p in ring]
    clat, clng = (min(lats) + max(lats)) / 2, (min(lngs) + max(lngs)) / 2
    radius = max(miles_between(clat, clng, lat, lng) for lng, lat in ring) + 0.5
    return clat, clng, radius


def inside(lat, lng, ring) -> bool:
    """Ray-casting point-in-polygon test."""
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def fetch(lat: float, lng: float, radius: float) -> list[dict]:
    query = urllib.parse.urlencode({
        "lat": lat,
        "lng": lng,
        "fuel_type": "diesel",
        "radius": round(radius, 2),
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


def to_rows(stations: list[dict], ring) -> list[list]:
    rows = []
    for s in stations:
        if s.get("temporary_closure") or s.get("permanent_closure"):
            continue
        price = s.get("price_diesel")
        if price is None:
            continue
        if s.get("lat") is None or s.get("lng") is None:
            continue
        if not inside(float(s["lat"]), float(s["lng"]), ring):
            continue
        reported = (s.get("price_last_updated_iso") or "")[:10]
        rows.append([
            tidy(s.get("name", "")),
            s.get("postcode", ""),
            f"{float(price):.1f}",
            s.get("brand", ""),
            tidy(s.get("address", "")),
            reported,
            f"{float(s['lat']):.5f}",
            f"{float(s['lng']):.5f}",
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
        "| " + " | ".join(COLUMNS[:README_COLUMNS]) + " |",
        "|" + "|".join(["---"] * README_COLUMNS) + "|",
    ]
    for r in rows:
        cells = list(r[:README_COLUMNS])
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
    ring = load_area()
    clat, clng, radius = search_circle(ring)
    print(f"Searching {radius:.1f} miles around the middle of the area")
    stations = fetch(clat, clng, radius)
    rows = to_rows(stations, ring)
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
