# All Points North -- Website, EPK & Growth Strategy

This repository contains the band's public-facing Electronic Press Kit website, growth strategy documentation, and automation tools.

**Live EPK**: [allpointsnorthband-art.github.io/.github.io](https://allpointsnorthband-art.github.io/.github.io/)

---

## Repository Structure

```
.github.io/
├── .github/workflows/
│   └── update-stats.yml              # GitHub Action: auto-updates EPK stats weekly
│
├── artwork/                           # Album & single cover art
├── files/                             # Technical rider (PDF, XLSX)
├── photos/                            # Press & live photos
├── scripts/
│   └── update_epk_stats.py           # EPK stats updater (used by GitHub Action)
│
├── strategy/                          # Band growth strategy & playbooks
│   ├── README.md                      # Strategy hub -- start here
│   ├── guides/
│   │   ├── 01-spotify-engine.md       # Spotify optimization, Canvas, editorial pitch
│   │   ├── 02-content-engine.md       # Instagram Reels strategy, batch workflow
│   │   ├── 03-playlist-outreach.md    # Curator pitching, SubmitHub, tracking
│   │   ├── 05-fan-community.md        # Email list, Mailchimp, Reddit, forums
│   │   ├── 06-press-outreach.md       # Blog/magazine targets, press templates
│   │   ├── 07-networking.md           # Peer bands, cross-promotion, playlists
│   │   ├── 08-automation-setup.md     # Free SaaS tools, weekly 90-min workflow
│   │   ├── 09-epk-fixes.md           # EPK website improvements
│   │   ├── 10-release-calendar.md     # 12-month timeline, 48-hour launch playbook
│   │   └── 11-automation-blueprints.md # Custom automation architecture
│   ├── databases/
│   │   └── dutch-venues-festivals.md  # 50+ venues, festivals, competitions (NL/BE/DE/UK)
│   └── templates/
│       ├── pitch-templates.md         # 12 copy-paste pitch emails & DMs
│       ├── tracking-spreadsheet-setup.md # Google Sheets tab templates
│       └── instagram-bio-linktree.md  # Bio copy, Linktree, hashtag presets
│
├── tools/                             # Python automation scripts
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # API credentials template
│   ├── playlist_scout.py              # Find Spotify playlists to pitch to
│   ├── metrics_collector.py           # Weekly Spotify metrics report
│   ├── update_epk_stats.py           # Update EPK HTML with live data
│   ├── reddit_listener.py            # Monitor Reddit for opportunities
│   ├── content_reposter.py           # Cross-platform caption generator
│   └── release_config.json           # Release day checklist config
│
├── index.html                         # EPK website (GitHub Pages)
└── README.md                          # This file
```

---

## Quick Start

### For the EPK Website

The website is served via GitHub Pages from `index.html`. Push changes to `main` to deploy.

### For the Growth Strategy

Start with `strategy/README.md` -- it provides a prioritized reading order and weekly workflow.

### For the Automation Tools

```bash
cd tools
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in API credentials (see below)
```

**Required credentials:**
- Spotify API: Register at [developer.spotify.com](https://developer.spotify.com/) (free)
- Reddit API: Register at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps/) (free, optional)

**GitHub Action setup** (for auto-updating EPK stats):
1. Go to repo Settings > Secrets and variables > Actions
2. Add `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
3. The Action runs every Monday at 06:00 UTC automatically

---

## Links

- [Spotify](https://open.spotify.com/artist/02lo7GheOKHi4dcjFhh46B)
- [Bandcamp](https://allpointsnorth.bandcamp.com/)
- [Instagram](https://www.instagram.com/allpointsnorth.band/)
- [Facebook](https://www.facebook.com/apnlive)
- [YouTube](https://www.youtube.com/channel/UC21YAJsZDA_rvj9bPUkJR_A)
- [Apple Music](https://music.apple.com/us/artist/all-points-north/1671344314)
