#!/usr/bin/env python3
"""Build the search area polygon (area.geojson).

The boundary runs:
  1. along the M56 from the M60 junction to the A538 junction (J6),
  2. in straight lines through the fixed corner points below,
  3. along the M60 from Bredbury (J25) back to the M56 junction.

The motorway sections are traced with the public OSRM routing service, which
follows OpenStreetMap roads. Run this by hand (Actions > Build search area)
only when the corners change; the daily price job just reads area.geojson.
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OSRM = "https://router.project-osrm.org/route/v1/driving/"

# (lat, lng)
M60_M56 = (53.4049, -2.2196)       # M60 J4 / M56 J1, Kingsway Interchange
M56_J3 = (53.3959, -2.2538)        # waypoint on the M56 at Sharston
M56_J5 = (53.3748, -2.2875)        # waypoint on the M56 at the airport junction
M56_A538 = (53.3622, -2.2962)      # M56 J6 / A538
CORNERS = [
    (53.2641, -2.2329),            # A34 / A537, Monks Heath
    (53.2415, -2.1267),            # Macclesfield Audi, Star Lane
    (53.3088, -2.0826),            # Pott Hall, Pott Shrigley
    (53.3703, -2.0994),            # A6 / A555
]
M60_BREDBURY = (53.4229, -2.1220)  # M60 J25, Bredbury
M60_STOCKPORT = (53.4105, -2.1612) # waypoint on the M60 through Stockport


def route(*points):
    coords = ";".join(f"{lng},{lat}" for lat, lng in points)
    url = f"{OSRM}{coords}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={"User-Agent": "diesel-prices area builder"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    if data.get("code") != "Ok":
        raise SystemExit(f"OSRM error: {data}")
    r = data["routes"][0]
    print(f"route {len(points)} pts: {r['distance']/1609.34:.1f} miles, {len(r['geometry']['coordinates'])} vertices")
    return r["geometry"]["coordinates"]  # [lng, lat]


def progress_along(pt, ref):
    """Distance along the reference polyline `ref` ([lng, lat] points) of the
    point on it nearest to `pt`, in rough flat units (fine at this scale)."""
    k = 0.6  # cos(53 deg): squash longitude so distances are roughly even
    px, py = pt[0] * k, pt[1]
    best_d, best_s, run = None, 0.0, 0.0
    for (ax, ay), (bx, by) in zip(ref, ref[1:]):
        ax, bx = ax * k, bx * k
        dx, dy = bx - ax, by - ay
        seg = (dx * dx + dy * dy) ** 0.5
        t = 0.0 if seg == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (seg * seg)))
        cx, cy = ax + t * dx, ay + t * dy
        d = (px - cx) ** 2 + (py - cy) ** 2
        if best_d is None or d < best_d:
            best_d, best_s = d, run + t * seg
        run += seg
    return best_s


def one_way(coords, waypoints):
    """Drop the doubling-back that routing does around junctions, keeping only
    points that move further along the motorway than any point before them."""
    ref = [[lng, lat] for lat, lng in waypoints]
    kept, best = [], -1.0
    for p in coords:
        s = progress_along(p, ref)
        if s > best:
            kept.append(p)
            best = s
    print(f"  kept {len(kept)} of {len(coords)} vertices")
    return kept


def main():
    ring = []
    m56 = [M60_M56, M56_J3, M56_J5, M56_A538]
    ring += one_way(route(*m56), m56)
    ring += [[lng, lat] for lat, lng in CORNERS]
    m60 = [M60_BREDBURY, M60_STOCKPORT, M60_M56]
    ring += one_way(route(*m60), m60)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    geo = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "Diesel price search area"},
            "geometry": {"type": "Polygon", "coordinates": [[[round(x, 6), round(y, 6)] for x, y in ring]]},
        }],
    }
    (ROOT / "area.geojson").write_text(json.dumps(geo), encoding="utf-8")
    print(f"Wrote area.geojson with {len(ring)} points")


if __name__ == "__main__":
    main()
