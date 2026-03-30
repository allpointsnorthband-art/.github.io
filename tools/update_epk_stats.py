"""
EPK Auto-Stats Updater -- Updates the EPK website with live Spotify data.

Reads the EPK index.html, fetches current Spotify follower count and popularity,
and rewrites the animateCounter() values. Designed to run via GitHub Action on a
weekly cron schedule.

Usage:
    python update_epk_stats.py --html-path ../index.html
    python update_epk_stats.py --html-path ../index.html --dry-run
"""

import argparse
import logging
import os
import re
import sys
from typing import Optional

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

ARTIST_ID: str = os.getenv("SPOTIFY_ARTIST_ID", "02lo7GheOKHi4dcjFhh46B")


def get_spotify_client() -> spotipy.Spotify:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set")
        sys.exit(1)

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def fetch_stats(sp: spotipy.Spotify) -> dict[str, int]:
    """Fetch current artist stats from Spotify."""
    artist = sp.artist(ARTIST_ID)
    followers = artist.get("followers", {}).get("total", 0)
    popularity = artist.get("popularity", 0)

    top_tracks = sp.artist_top_tracks(ARTIST_ID, country="NL")
    total_popularity = sum(
        t.get("popularity", 0) for t in top_tracks.get("tracks", [])
    )

    stream_estimate = max(followers * 20, 1000)

    return {
        "spotify_followers": followers,
        "popularity": popularity,
        "stream_estimate": stream_estimate,
    }


def update_html(html_path: str, stats: dict[str, int], dry_run: bool = False) -> bool:
    """Update the animateCounter() calls in index.html with live data."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    spotify_val = max(stats["spotify_followers"], 50)

    pattern_spotify = r"(animateCounter\('stat-spotify',\s*)\d+"
    pattern_streams = r"(animateCounter\('stat-streams',\s*)\d+"

    new_content = content
    new_content = re.sub(pattern_spotify, rf"\g<1>{spotify_val}", new_content)
    new_content = re.sub(pattern_streams, rf"\g<1>{stats['stream_estimate']}", new_content)

    if new_content == content:
        logger.info("No changes needed -- stats are already current")
        return False

    if dry_run:
        logger.info("DRY RUN -- would update:")
        logger.info("  stat-spotify: %d", spotify_val)
        logger.info("  stat-streams: %d", stats["stream_estimate"])
        return False

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    logger.info("Updated %s:", html_path)
    logger.info("  stat-spotify: %d", spotify_val)
    logger.info("  stat-streams: %d", stats["stream_estimate"])
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Update EPK stats from Spotify data")
    parser.add_argument(
        "--html-path",
        type=str,
        default="index.html",
        help="Path to the EPK index.html file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    if not os.path.exists(args.html_path):
        logger.error("HTML file not found: %s", args.html_path)
        sys.exit(1)

    sp = get_spotify_client()

    logger.info("Fetching stats from Spotify...")
    stats = fetch_stats(sp)
    logger.info("  Followers: %d", stats["spotify_followers"])
    logger.info("  Popularity: %d/100", stats["popularity"])
    logger.info("  Stream estimate: %d", stats["stream_estimate"])

    changed = update_html(args.html_path, stats, dry_run=args.dry_run)

    if changed:
        logger.info("Stats updated successfully. Commit and push to deploy.")
    else:
        logger.info("No changes to deploy.")


if __name__ == "__main__":
    main()
