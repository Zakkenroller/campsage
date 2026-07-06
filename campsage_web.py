#!/usr/bin/env python3
"""
campsage_web.py — standalone web UI for CampSage. Serves the phone status page + the interactive
map (Leaflet + OpenStreetMap, no API keys). Reads the scan output that camp_agent.py writes to
DATA_DIR. Run:  python campsage_web.py   (then open http://localhost:5001/camp)

For the hosted (static) build see build_site.py — the map itself is rendered by mapbuild.py,
which both this route and the static build share.
"""
import json
from pathlib import Path
from flask import Flask, jsonify, Response

import config
from mapbuild import render_map_html

DATA = config.DATA_DIR
app = Flask(__name__)


@app.route("/")
@app.route("/camp")
def camp_page():
    f = DATA / "dashboard.html"
    if f.exists():
        return f.read_text()
    return ("<body style='font:16px sans-serif;padding:40px'>CampSage hasn't run yet — "
            "run camp_agent.py first.</body>", 200)


@app.route("/camp/data")
def camp_data():
    f = DATA / "status.json"
    if f.exists():
        return Response(f.read_text(), mimetype="application/json")
    return jsonify({"status": "pending"}), 200


@app.route("/camp/map")
def camp_map():
    """Self-contained Leaflet map of every available campsite + beach (OSM tiles, no API keys)."""
    return Response(render_map_html(DATA, list_href="/camp"), mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
