"""
CampSage configuration.

A small, dependency-free agent that hunts recreation.gov for great California
campsites with 2-3 consecutive nights open at the SAME site, ranked closest-first
among well-reviewed spots, and publishes a phone-friendly status page.

Everything tunable lives here. Edit + re-run camp_agent.py (or wait for cron).
"""
from pathlib import Path

# ── Where "closest" is measured from (home base for drive distance) ───────────
HOME_NAME = "Napa"
HOME_LAT  = 38.2975
HOME_LNG  = -122.2869

# ── How far you'll drive + how good a spot has to be ──────────────────────────
SEARCH_RADIUS_MI = 175      # recreation.gov search radius (miles)
MAX_DISTANCE_MI  = 175      # hard cap: drop anything farther than this
                            # (175 reaches Tahoe / Gold Country / the Mendocino coast from Napa)
MIN_RATING       = 4.0      # only "good reviews" — average stars >= this
MIN_REVIEWS      = 4        # ...backed by at least this many ratings (signal, not noise)

# A second, lower bar so genuinely great but lightly-reviewed gems still surface,
# clearly flagged as "few reviews". Set EQUAL to the above to disable the tier.
SOFT_MIN_RATING  = 4.5      # a 4.5★+ spot with only a couple reviews can still show
SOFT_MIN_REVIEWS = 1

# ── The trip you want ─────────────────────────────────────────────────────────
WINDOW_DAYS   = 60          # search this many days out from today
NIGHTS        = [3, 2]      # acceptable consecutive-night blocks (prefer 3, accept 2)
WEEKENDS_ONLY = False       # True => only blocks that include a Fri or Sat night

# ── Beach section (MAINLAND drive-up state beaches via ReserveCalifornia) ─────
# These are the iconic CA ocean beach campgrounds (Leo Carrillo, San Onofre, Carpinteria,
# El Capitán, Refugio, Pismo, …). They live on ReserveCalifornia, NOT recreation.gov, and
# the system has no review/star scores — so the beach section is ranked by distance + soonest.
# Channel Islands (boat-in) are deliberately NOT here — the user doesn't want island camping.
BEACH_ENABLED      = True
BEACH_MAX_DISTANCE = 600     # miles from home; statewide — the whole CA coast, Mendocino to San Diego
# A ReserveCalifornia place is "beach camping" if its name ends in " SB" (State Beach) or
# contains the word Beach, or is one of these coastal State Parks that have camping…
# (Sonoma Coast SB, Half Moon Bay SB, Carpinteria SB, Refugio SB, El Capitán SB, … match by name;
# these coastal State Parks up and down the state are added explicitly.)
BEACH_ALLOW = (
    # NorCal / Central coast
    "Salt Point SP", "MacKerricher SP", "Van Damme SP", "Russian Gulch SP", "Manchester SP",
    "Sue-meg SP", "Bodega Dunes", "Wrights Beach", "Montana De Oro SP", "Morro Bay SP",
    # SoCal coast
    "Leo Carrillo SP", "Point Mugu SP", "Crystal Cove SP Moro Campground", "Gaviota SP",
    "San Onofre SB", "Doheny SB", "South Carlsbad SB", "Silver Strand SB")
# …but never these (inland, lakes, cottages/trailers, off-highway dune areas).
BEACH_VETO  = ("Cottages", "Trailers", "Lake", "SRA", "SVRA", "SHP", "Reservoir", "Desert")

# ── Output / ranking ──────────────────────────────────────────────────────────
TOP_N_DISPLAY = 30          # max campgrounds to render on the page
DEFAULT_SORT  = "distance"  # "distance" (closest first) | "rating" | "soonest"
SHOW_ONLY_OPENINGS = True   # only show places with an actual 2-3 night block; hide full ones entirely
                            # (beaches + the "great but full" alert list). Set False to show full places.

# ── Destination regions (tabs) ────────────────────────────────────────────────
# Each campground is tagged with the NEAREST of these anchors (by lat/lng), so the page
# can show a tab per place (Big Bear, Tahoe, …). Only regions that actually have campgrounds
# in range appear as tabs. Add an anchor here to split/merge a region.
#
# STATEWIDE: these anchors blanket ALL of California so every major camping destination
# surfaces under its tab. Home stays Napa (distance/directions are measured from there), so the
# "All" tab still shows the closest spots first; the region tabs let you reach anywhere in CA.
REGION_ANCHORS = [
    # ── Bay Area / North Coast ──
    ("Napa / Sonoma Valley",        38.400, -122.450),  # Bothe-Napa Valley, Sugarloaf Ridge
    ("Lake Berryessa",              38.600, -122.230),
    ("Point Reyes / Marin",         38.040, -122.800),
    ("Sonoma Coast",                38.400, -123.070),   # Bodega Dunes, Wright's Beach, Jenner
    ("Russian River / Guerneville", 38.500, -123.000),
    ("Clear Lake",                  39.030, -122.760),
    ("Anderson Valley / Hendy Woods", 39.075, -123.470),
    ("Mendocino Coast",             39.310, -123.800),   # MacKerricher, Van Damme, Russian Gulch
    ("Humboldt Redwoods / Redwoods", 40.310, -123.900),
    # ── Far North ──
    ("Shasta / Trinity",            41.000, -122.400),
    ("Lassen Volcanic",             40.490, -121.500),
    ("Lava Beds / Modoc",           41.710, -121.510),
    # ── Sierra / Eastern ──
    ("Gold Country / Auburn",       38.900, -121.080),   # Sierra foothills, American River
    ("Plumas / Feather River",      39.940, -120.950),
    ("Lake Tahoe (North)",          39.170, -120.140),
    ("Lake Tahoe (South)",          38.940, -119.980),
    ("Yosemite",                    37.865, -119.538),
    ("Mammoth / Eastern Sierra",    37.650, -118.970),
    ("Sequoia & Kings Canyon",      36.600, -118.700),
    # ── Central Coast ──
    ("Big Basin / Santa Cruz Mtns", 37.170, -122.220),
    ("Pinnacles",                   36.490, -121.180),
    ("Monterey / Big Sur",          36.270, -121.800),
    ("San Luis Obispo / Pismo",     35.130, -120.630),
    ("Santa Barbara / Los Padres",  34.550, -119.800),
    # ── Southern California ──
    ("Ojai / Los Padres",           34.490, -119.250),
    ("Malibu / Ventura Coast",      34.050, -118.950),
    ("San Gabriels / Angeles",      34.300, -118.020),
    ("Big Bear",                    34.244, -116.911),
    ("Lake Arrowhead",              34.249, -117.189),
    ("Idyllwild / San Jacinto",     33.745, -116.716),
    ("Orange County Coast",         33.460, -117.660),
    ("San Diego Coast",             33.050, -117.290),
    ("Julian / Cuyamaca",           32.960, -116.600),
    # ── Desert ──
    ("Joshua Tree",                 34.000, -116.160),
    ("Anza-Borrego Desert",         33.270, -116.410),
    ("Death Valley",                36.500, -117.100),
    ("Mojave National Preserve",    35.140, -115.510),
]

# Far destinations sit beyond the everyday home radius and the recreation.gov search's
# ~150-result score cap, so a single home-centered search never returns them. CampSage
# therefore ALSO runs a small search centered on each anchor and merges the results. The
# "All" tab stays closest-to-home (≤ MAX_DISTANCE_MI); farther finds appear under their region tab.
ANCHOR_SEARCH_ENABLED   = True
REGION_SEARCH_RADIUS_MI = 60    # radius for each per-anchor destination search (covers the
                                # full ~50mi span of a region, e.g. Plaskett Creek south of Big Sur)
REGION_MAX_DISTANCE_MI  = 600   # absolute outer cap for any destination find — 600mi reaches
                                # San Diego / Death Valley / Modoc from Napa, i.e. the whole state
REGION_MAX_PER_TAB      = 12    # cap destination campgrounds kept per far region tab

# ── State parks (ReserveCalifornia, beyond the beach section) ─────────────────
# Pull general CA STATE PARK campgrounds (Pfeiffer Big Sur, Andrew Molera, Limekiln, …) —
# NOT on recreation.gov — and merge them into the region tabs + a 🏕️ State Parks tab.
# Searched per region anchor (same pattern as the federal anchor search). No review scores
# exist in ReserveCalifornia, so these rank by distance/soonest like the beaches do.
STATE_PARKS_ENABLED    = True
STATE_PARK_PER_ANCHOR  = 6      # nearest campable state parks kept per region (bounds API load)
STATE_PARK_MAX_ANALYZE = 70     # global cap on parks we fetch availability for (API budget;
                                # raised for statewide coverage across many more anchors)

# ── Plumbing ──────────────────────────────────────────────────────────────────
DATA_DIR      = Path.home() / "campsage"
STATUS_JSON   = DATA_DIR / "status.json"
DASHBOARD_HTML= DATA_DIR / "dashboard.html"
TIPS_JSON     = DATA_DIR / "booking_tips.json"   # written by ai_concierge.sh (subscription)
HEALTH_JSON   = DATA_DIR / "health.json"          # written by campsage_doctor.sh (subscription)
LOG_FILE      = DATA_DIR / "campsage.log"

# Browser-like UA — recreation.gov's public JSON endpoints answer these; a bare
# python UA can get an HTML interstitial or a block.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

HTTP_TIMEOUT  = 30
MAX_WORKERS   = 8           # parallel availability fetches (be polite)
RETRIES       = 3
