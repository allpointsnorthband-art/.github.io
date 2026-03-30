# All Points North -- Growth Strategy

A comprehensive action plan for growing All Points North from near-zero to a recognized act in the progressive rock scene. Designed for zero budget and 1-3 hours/week of promotion time.

## Quick Start (Do This First)

1. Read `guides/01-spotify-engine.md` -- complete the Spotify for Artists checklist (1 hour)
2. Read `guides/08-automation-setup.md` -- set up the free tool stack (90 min one-time)
3. Read `guides/02-content-engine.md` -- start the Instagram Reels routine (45 min/week)
4. Create the tracking spreadsheet from `templates/tracking-spreadsheet-setup.md` (15 min)

## Directory Structure

This strategy lives inside the band's main GitHub repo at `strategy/`.

```
strategy/                              <- You are here
├── README.md                          <- Strategy hub -- start here
├── guides/
│   ├── 01-spotify-engine.md           <- Spotify optimization, Canvas, playlists, editorial pitch
│   ├── 02-content-engine.md           <- Instagram Reels strategy, batch workflow
│   ├── 03-playlist-outreach.md        <- Curator pitching, SubmitHub, tracking
│   ├── 05-fan-community.md            <- Email list, Mailchimp, Reddit, forums
│   ├── 06-press-outreach.md           <- Blog/magazine targets, press templates
│   ├── 07-networking.md               <- Peer bands, cross-promotion, shared playlists
│   ├── 08-automation-setup.md         <- Free SaaS tools, weekly 90-min workflow
│   ├── 09-epk-fixes.md               <- EPK website improvements
│   ├── 10-release-calendar.md         <- 12-month timeline, 48-hour launch playbook
│   └── 11-automation-blueprints.md    <- Custom automation architecture
├── databases/
│   └── dutch-venues-festivals.md      <- Venue/festival/competition database (NL/BE/DE/UK)
└── templates/
    ├── pitch-templates.md             <- 12 copy-paste pitch emails & DMs
    ├── tracking-spreadsheet-setup.md  <- Google Sheets tab templates
    └── instagram-bio-linktree.md      <- Bio copy, Linktree setup, hashtag presets
```

Automation tools live in `../tools/` (sibling directory). See `guides/11-automation-blueprints.md` for architecture.

## Automation Tools

Python scripts in `../tools/` automate recurring tasks. Setup:

```bash
cd tools
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in Spotify API credentials
```

| Tool | What It Does | Run |
|---|---|---|
| `playlist_scout.py` | Finds 200-5K follower playlists to pitch | `python playlist_scout.py` |
| `metrics_collector.py` | Weekly Spotify metrics report | `python metrics_collector.py` |
| `update_epk_stats.py` | Updates EPK HTML with live Spotify data | Runs automatically via GitHub Action |
| `reddit_listener.py` | Scans Reddit for engagement opportunities | `python reddit_listener.py` |
| `content_reposter.py` | Generates TikTok/YouTube captions from Reels | `python content_reposter.py --input video.mp4` |

**GitHub Action**: `.github/workflows/update-stats.yml` runs every Monday, fetches Spotify data, and auto-commits updated stats to the EPK website.

## Weekly Rhythm (90 minutes)

| Day | Time | Action |
|---|---|---|
| Sunday | 45 min | Batch-create 2-3 Reels, schedule for the week |
| Wednesday | 30 min | Pitch 3-5 playlist curators, respond to DMs/comments |
| Friday | 15 min | Check Spotify for Artists, post a Story |
| 1st Tuesday/month | +30 min | Send newsletter, update metrics spreadsheet |

## 12-Month Targets

| Metric | Target |
|---|---|
| Spotify monthly listeners | 500-2,000 |
| Instagram followers | 300-800 |
| Shows (NL) | 8-15 |
| Shows (BE/DE) | 2-3 |
| Email subscribers | 100-300 |
| Playlist placements | 15-30 |
