# CampSage 🏕️

Finds great **California** campsites with **2–3 consecutive nights open at the same site**,
ranked **closest-to-home first** among **well-reviewed** spots, and publishes a phone-friendly
status page + an interactive map. **No API keys.**

Currently tuned for a **Napa, CA** home base (Northern California regions: Sonoma/Mendocino coast,
Tahoe, Gold Country, Yosemite, the redwoods…). Change `HOME_*` + `REGION_ANCHORS` + `BEACH_ALLOW`
in `config.py` to re-home it anywhere. It runs on a schedule via **GitHub Actions** and publishes a
**static site to Netlify** — no server to keep alive (see **Deploy** below).

## Quick start
```bash
pip install flask                 # the only dependency (scanner itself is stdlib-only)
# 1. set your home location + search radius in config.py (HOME_LAT / HOME_LNG / ...)
python3 camp_agent.py             # scan recreation.gov + ReserveCalifornia -> writes status.json
python3 camp_wiki_images.py       # (optional) fetch beach/park photos from Wikimedia Commons
python3 campsage_web.py           # serve it -> open http://localhost:5001/camp  (and /camp/map)
```
Run `camp_agent.py` on a cron (e.g. a few times a day) to keep results fresh. Add the page to your
phone's Home Screen. Every card has a green **Book on Recreation.gov →** button, a **See calendar**
link, and **Directions**.

## The map (`/camp/map`)
Interactive Leaflet map (OpenStreetMap tiles, **no key**) of every open site — filter by
type / nights / weekend / sought-after / region; tap a pin for photos, the exact **open dates + site
numbers**, and a booking link. Beach/state-park photos come from Wikimedia Commons (keyless).

## Place tabs
A scrollable tab strip groups every campground by **destination region** (Big Bear, Lake Arrowhead,
Ojai, Orange County Coast, …). Each campground is tagged with its nearest anchor in
`config.REGION_ANCHORS` by lat/lng; only regions that have campgrounds in range become tabs,
ordered closest-first. Tabs: **All** · **🏖️ Beaches** · one per region. A 📍 chip on each card
shows its region. All cards live in one `#grid`; tabs filter, the sort bar sorts.

## Social score (number + stars)
Every card shows a **social buzz** score — a 0–5 number + stars derived from YouTube (how many
videos + total views for "<name> camping"), via `socialscore.py`. It's POPULARITY, not
satisfaction, and labelled that way. Live Reddit/IG/TikTok scraping is impossible (they 403
datacenter IPs), so this is the honest no-key signal; scores are cached ~2 weeks so the scan stays
light. Sortable via the "Social buzz" button. Plus the 💬 Reviews link row (Reddit/YouTube/TikTok/
Google searches) per card.

## Sections on the page
1. **⛰️ All campgrounds** — 2–3 night openings, closest-to-LA first. Sort: Closest /
   Best reviewed / Most reviewed / Highest rated / Soonest.
2. **🏖️ Beach camping — state beaches** — MAINLAND drive-up California state beaches
   (Leo Carrillo, San Onofre, Carpinteria, El Capitán, Refugio, Pismo, …) via **ReserveCalifornia**.
   Island camping is excluded. The state-park system has no review scores, so this ranks by
   **closest** + **soonest** + **most sites open**. Own sort bar; Book button → ReserveCalifornia.
3. **🧭 Booking concierge** + **Also great nearby — currently full**.

The beach source is `reservecalifornia.py` — it reverse-maps the same RDR API the
reservecalifornia.com site uses (`search/place` for nearby parks + distance, `search/grid` for
per-night `IsFree` availability). No API key. Base URL is read from the site's own config.json.

"Best reviewed" = `rating × log10(reviews+1)` — credibility-weighted, so a 4.7★/986-review spot
beats a 4.6★/5-review one. "Most reviewed" = raw count.

**Social reviews:** every card has a 💬 Reviews row (Reddit / YouTube / TikTok / Google) that
opens a search pre-filled with the campground name. These are deep links, not scraped — Reddit,
Instagram, and TikTok all 403 datacenter IPs, so live fetching is impossible/unreliable; the
links open on the phone where the user is logged in and get real results every time.

## How it works
- **Data:** recreation.gov public JSON — `search` (ratings, review counts, drive distance,
  lat/lng) + `availability` (per-night status per site, so consecutive nights are detectable).
- `camp_agent.py` discovers campgrounds within `MAX_DISTANCE_MI` of `HOME_*`, keeps the
  well-reviewed ones (`MIN_RATING`/`MIN_REVIEWS`, plus a high-rating "gem" tier), fetches each
  campground's availability across the window in parallel, finds each site's earliest run of
  2–3 available nights, ranks closest-first, and writes:
  - `~/campsage/status.json` — machine-readable results
  - `~/campsage/dashboard.html` — the self-contained page served at `/camp`
- `ai_concierge.sh` asks Claude (on the **subscription**, no API cost) for booking tips specific
  to the current top spots → `~/campsage/booking_tips.json` (shown under "Booking concierge").

## Tuning
Everything is in `config.py`: home base (`HOME_NAME`/`HOME_LAT`/`HOME_LNG`), max distance, rating
bars, window length, nights (`NIGHTS=[3,2]`), `WEEKENDS_ONLY`, the region tabs (`REGION_ANCHORS`),
and the beach list (`BEACH_ALLOW`). Edit and re-run `python3 camp_agent.py`.

## Deploy (GitHub Actions → Netlify) — no server needed
The scan output is a **static snapshot**, so there's nothing to keep running. GitHub Actions runs the
scan on a schedule and deploys a static site to Netlify:

1. `.github/workflows/scan.yml` runs `camp_agent.py` → `camp_wiki_images.py` → `build_site.py` on a
   cron (~7am / 1pm / 6pm Pacific) and on manual trigger.
2. `build_site.py` assembles `./public/` — `index.html` (the dashboard), `map.html` (the interactive
   map, data baked in), `status.json`, and `_redirects` (so `/camp` and `/camp/map` still resolve).
3. The workflow deploys `./public` to Netlify.

**One-time setup** (≈5 min):
1. Create a Netlify site (empty is fine): **app.netlify.com → Add new site → Import an existing
   project**, or `netlify sites:create`. Note its **Site ID** (Site settings → General → Site ID).
2. Create a Netlify **personal access token**: **User settings → Applications → New access token**.
3. In this GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `NETLIFY_AUTH_TOKEN` = the token from step 2
   - `NETLIFY_SITE_ID` = the Site ID from step 1
4. Go to the repo's **Actions** tab → **Scan & publish CampSage** → **Run workflow** to publish now.
   After that it runs itself on the schedule.

> **Note:** recreation.gov / ReserveCalifornia occasionally block datacenter IPs. If a scheduled run
> gets no data, the run logs will show it — the fix is to run the same workflow on a self-hosted
> runner (e.g. a home machine or Raspberry Pi) instead of GitHub's shared runners.

## Run it locally
```bash
pip install -r requirements.txt
python3 camp_agent.py         # scan → writes ~/campsage/status.json + dashboard.html
python3 camp_wiki_images.py   # (optional) park/beach photos
python3 campsage_web.py       # serve → http://localhost:5001/camp  (and /camp/map)
# or build the static site the way Netlify gets it:
python3 build_site.py         # → ./public/{index.html, map.html, ...}
```

## Validate
`python3 selftest.py` — checks the live API, freshness, sort/distance/rating/nights invariants,
that a claimed opening is *independently* still available, `/camp` serves, and cron is installed.
Exit 0 = all pass.

## Notes
- Single-site **group** campgrounds can show "1 site open" and get booked in minutes — book fast.
- Coverage is recreation.gov (national forests, NPS, etc.). California **state parks**
  (ReserveCalifornia) are a separate system not yet included — a future add.
