# Automation Blueprints -- Build Technology to Run on Autopilot

**Band**: All Points North
**Goal**: Reduce the 90 min/week manual effort further by automating recurring tasks with custom-built tools, scripts, and scheduled workflows.

---

## Architecture Overview

Three tiers of automation, ordered by impact and implementation effort.

```
Tier 1: Build Now (free, 1-2 hours each)
├── EPK Auto-Stats Updater      GitHub Action + Python -- auto-updates website stats weekly
├── Playlist Scout               Python CLI -- discovers playlists to pitch to
├── Metrics Collector            Python CLI -- pulls all platform data into one report
└── Release Day Checklist Bot    GitHub Action -- sends step-by-step reminders on release day

Tier 2: Build When Ready (free, 2-4 hours each)
├── Reddit Listener              Python + PRAW -- monitors subreddits for opportunities
├── Cross-Platform Reposter      Python CLI -- reformats content for TikTok/YouTube Shorts
└── Pitch Follow-Up Automator    Python -- auto-sends follow-ups for unanswered pitches

Tier 3: Build When Budget Allows (low cost, half-day each)
├── n8n Workflow Hub             Self-hosted -- full multi-platform automation engine
├── AI Content Generator         OpenAI API -- generates captions, bios, pitch variations
└── Fan Engagement Dashboard     Web app -- real-time metrics across all platforms
```

---

## Tier 1: Build Now

### 1. EPK Auto-Stats Updater

**What it does**: A GitHub Action runs weekly, scrapes the latest Spotify follower count and
other metrics, updates the EPK `index.html` with real numbers, and commits the change automatically.
The EPK website always shows current data without anyone touching it.

**How it works**:
1. GitHub Action triggers on a cron schedule (every Monday at 6:00 UTC)
2. Python script uses `spotifyscraper` or the Spotify Web API (via `spotipy`) to fetch artist data
3. Script reads `index.html`, finds the `animateCounter()` calls, and replaces the target values
4. Git commit + push -- GitHub Pages auto-deploys

**Files created**:
- `.github/workflows/update-stats.yml` -- the GitHub Action workflow
- `scripts/update_epk_stats.py` -- the Python script

**Setup**:
1. Get a Spotify API client ID and secret from developer.spotify.com
2. Add them as GitHub repository secrets: `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
3. Push the workflow file and script to the EPK repo
4. The Action runs automatically every Monday

**See**: `tools/update_epk_stats.py` and `../apn-epk/.github/workflows/update-stats.yml`

---

### 2. Playlist Scout

**What it does**: A Python CLI tool that searches Spotify for playlists matching progressive rock / metal
keywords, filters by follower count (200-5,000), checks if they were recently updated, and outputs
a list of curators to pitch. Saves hours of manual searching.

**How it works**:
1. Uses `spotipy` (Spotify Web API) to search for playlists by keyword
2. Filters results: follower count range, last updated within 30 days, not official Spotify playlists
3. Extracts curator name, playlist URL, follower count, track count, description
4. Outputs a CSV or appends to the Google Sheets tracker

**Usage**:
```bash
python playlist_scout.py --genre "progressive rock" --min-followers 200 --max-followers 5000
```

**See**: `tools/playlist_scout.py`

---

### 3. Metrics Collector

**What it does**: A single Python script that pulls data from Spotify (via API), and outputs
a weekly summary. Run it manually or on a cron schedule. Populates the Google Sheets metrics tab
or prints a report to the terminal.

**Data collected**:
- Spotify: followers, monthly listeners (via scraper), top tracks, recent playlist additions
- Instagram: follower count (via public profile scrape -- no API key needed)

**Usage**:
```bash
python metrics_collector.py
```

**Output example**:
```
=== APN Weekly Metrics Report (2026-04-07) ===
Spotify Followers:      142
Spotify Monthly Listen: 156
Top Track:              Sargassum (423 streams)
Instagram Followers:    87
New Playlists This Week: 2
```

**See**: `tools/metrics_collector.py`

---

### 4. Release Day Checklist Bot

**What it does**: A GitHub Action that, on a manually specified release date, sends a series of
timed email reminders throughout the day with the exact actions from the 48-Hour Launch Playbook.

**How it works**:
1. You set the release date in a config file (`release_config.json`)
2. GitHub Action triggers on that date
3. Sends emails via a free SMTP service (Gmail) at scheduled intervals:
   - 8:00 AM: "Track is live! Post Reel now. CTA: Save this track."
   - 10:00 AM: "Send newsletter via Mailchimp."
   - 12:00 PM: "Post on Facebook."
   - 2:00 PM: "Post on Reddit."
   - 6:00 PM: "Post Instagram Story #2."
   - Next day 9:00 AM: "Check Spotify for Artists. Submit to SubmitHub."

**Alternative**: Use a simple cron job or Google Apps Script with Google Calendar triggers if
GitHub Actions feels heavy for this use case.

**See**: `tools/release_config.json` and `../apn-epk/.github/workflows/release-day.yml`

---

## Tier 2: Build When Ready

### 5. Reddit Listener

**What it does**: A Python script using PRAW (Python Reddit API Wrapper) that monitors
r/progmetal, r/progrockmusic, r/listentothis, and r/SpotifyPlaylists for posts where
APN could contribute. Sends a Telegram or email notification when it finds something.

**Triggers**:
- New posts mentioning "progressive rock" + "Netherlands" or "Dutch"
- "Playlist" threads in prog subreddits (curator discovery)
- Weekly self-promotion threads (reminder to post)
- Posts asking for band recommendations in the prog/metal genre

**Not automated**: The actual posting/commenting. Reddit punishes bot behavior and self-promotion.
This tool surfaces opportunities; a human responds.

**Setup**: Requires a Reddit API application (free) at reddit.com/prefs/apps.

---

### 6. Cross-Platform Reposter

**What it does**: Takes a finished Instagram Reel (video file) and generates platform-optimized
versions for TikTok and YouTube Shorts:
- Strips Instagram watermark (if downloading from IG)
- Adds platform-appropriate text overlays
- Generates platform-specific captions from templates
- Outputs files ready to upload

**Tech**: Python + `ffmpeg` for video processing, Jinja2 for caption templates.

---

### 7. Pitch Follow-Up Automator

**What it does**: Reads the Google Sheets pitch tracker, finds submissions older than 10 days
with status "Pending", and drafts follow-up emails. Does NOT send automatically -- generates
drafts in Gmail for human review and sending.

**Why not fully auto-send**: Curators and press contacts are humans. Auto-sent follow-ups that
feel robotic burn bridges. This tool does the bookkeeping; you add the human touch.

---

## Tier 3: Build When Budget Allows

### 8. n8n Workflow Hub

**What it does**: A self-hosted n8n instance (free, runs on any VPS) that orchestrates
multi-platform automation:

**Workflow 1: "New Release Pipeline"**
```
Trigger: New track appears on Spotify (Spotify webhook)
→ Generate social media posts (AI node)
→ Post to Instagram, Facebook, Twitter (platform nodes)
→ Send newsletter (Mailchimp node)
→ Submit to SubmitHub (HTTP request node)
→ Log to Google Sheets (tracking node)
→ Send Telegram notification: "Release day automation complete"
```

**Workflow 2: "Weekly Metrics Report"**
```
Trigger: Every Monday 9:00 AM
→ Pull Spotify data (HTTP request)
→ Pull Instagram data (HTTP request)
→ Format into report (function node)
→ Append to Google Sheets
→ Send summary via Telegram/Email
```

**Workflow 3: "Content Recycler"**
```
Trigger: Every 2 weeks
→ Check Spotify for Artists: which track has lowest streams
→ Generate a "rediscovery" social post template
→ Queue in Buffer
→ Log action
```

**Cost**: Free self-hosted, or $20/month for n8n Cloud (200 workflow executions).

---

### 9. AI Content Generator

**What it does**: Uses OpenAI API (or local LLM) to generate:
- Instagram captions from a one-line prompt ("Reel showing guitar riff from Sargassum")
- Personalized playlist pitch variations (input: curator name + playlist name, output: pitch email)
- Newsletter drafts from bullet points
- Bio variations for different contexts (festival app, press kit, social profile)

**Cost**: OpenAI API ~$0.01 per generation. 100 generations/month = ~$1.

---

### 10. Fan Engagement Dashboard

**What it does**: A lightweight web app (Go backend + HTML/Tailwind frontend, per your engineering
standards) that aggregates all metrics into a single real-time dashboard:

- Spotify: listeners, followers, streams, playlist placements
- Instagram: followers, Reel reach, engagement rate
- Email: subscribers, open rate, click rate (Mailchimp API)
- Shows: upcoming and past (manual input)
- Pitch tracker: pending, accepted, declined counts

**Why build this**: Google Sheets works for tracking, but a dedicated dashboard is faster to
glance at, can auto-refresh, and looks professional if you ever need to show metrics to a
venue, label, or festival organizer.

---

## Implementation Priority Matrix

| Automation | Impact | Effort | Dependencies | Priority |
|---|---|---|---|---|
| EPK Auto-Stats | High (always-current website) | 1 hour | Spotify API credentials | Do first |
| Playlist Scout | High (saves 30+ min/week) | 2 hours | Spotify API credentials | Do first |
| Metrics Collector | Medium (saves 15 min/week) | 1 hour | Spotify API credentials | Do first |
| Release Day Bot | High (prevents missed steps) | 1 hour | Gmail credentials | Do before next release |
| Reddit Listener | Medium (surfaces opportunities) | 2 hours | Reddit API app | Do in month 2 |
| Cross-Platform Reposter | Medium (saves 20 min/week) | 3 hours | ffmpeg installed | Do when expanding to TikTok |
| Pitch Follow-Up | Medium (saves 15 min/week) | 2 hours | Google Sheets API | Do in month 2 |
| n8n Hub | Very High (full orchestration) | Half day | VPS or n8n Cloud | Do in month 3+ |
| AI Content Generator | Medium (saves 20 min/week) | 1 hour | OpenAI API key ($1/mo) | Do when budget allows |
| Fan Dashboard | Low (nice-to-have) | 1 day | All APIs | Do when metrics justify it |

---

## Recurring Automation Schedule

Once all Tier 1 tools are running, the automated schedule looks like this:

| When | What Runs | How |
|---|---|---|
| Every Monday 6:00 UTC | EPK stats update | GitHub Action (auto) |
| Every Monday 9:00 UTC | Metrics report generated | Cron / GitHub Action (auto) |
| Every Wednesday | Playlist Scout results emailed | Cron / manual trigger |
| Release day | 48-hour checklist reminders | GitHub Action (auto) |
| Continuous | Reddit listener monitors for opportunities | Background process or cron |

**Remaining manual work after automation**:
- Content creation (filming clips at rehearsal) -- cannot be automated
- Actual playlist pitching (writing personalized DMs) -- should stay human
- Community engagement (commenting, replying) -- should stay human
- Live show booking (negotiation) -- should stay human

**Estimated time savings**: From 90 min/week manual to ~50 min/week, with better outcomes
because the scout and listener surface opportunities you'd otherwise miss.
