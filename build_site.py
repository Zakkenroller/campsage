#!/usr/bin/env python3
"""
build_site.py — assemble the static CampSage site into ./public for hosting (Netlify / any static host).

Run AFTER the scan:
    python3 camp_agent.py          # writes status.json + dashboard.html to DATA_DIR
    python3 camp_wiki_images.py    # (optional) writes wiki_images.json
    python3 build_site.py          # -> ./public/{index.html, map.html, status.json, wiki_images.json}

The scan output is a snapshot, so the whole site is static — no server needed at serve time.
GitHub Actions runs the three steps on a schedule and deploys ./public to Netlify (see
.github/workflows/scan.yml).
"""
import shutil
import sys
from pathlib import Path

import config
from mapbuild import render_map_html

DATA = config.DATA_DIR
OUT = Path(__file__).resolve().parent / "public"


def main():
    dash = DATA / "dashboard.html"
    if not dash.exists():
        sys.exit(f"ERROR: {dash} not found — run camp_agent.py first so there's a scan to publish.")

    OUT.mkdir(parents=True, exist_ok=True)

    # index.html = the dashboard, with its in-app map link retargeted to the static map file.
    html = dash.read_text().replace('href="/camp/map"', 'href="map.html"')
    (OUT / "index.html").write_text(html)

    # map.html = the interactive map, with its "← List" link pointing back at index.html.
    (OUT / "map.html").write_text(render_map_html(DATA, list_href="index.html"))

    # Publish the raw data too (handy for debugging / anyone who wants the JSON feed).
    for name in ("status.json", "wiki_images.json"):
        src = DATA / name
        if src.exists():
            shutil.copyfile(src, OUT / name)

    # Keep the old /camp and /camp/map URLs working on the static host (Netlify _redirects).
    (OUT / "_redirects").write_text(
        "/camp        /index.html   200\n"
        "/camp/map    /map.html     200\n"
    )

    files = sorted(p.name for p in OUT.iterdir())
    print(f"Built static site -> {OUT}")
    print("  " + "\n  ".join(files))


if __name__ == "__main__":
    main()
