"""
EPK Auto-Stats Updater -- runs via GitHub Actions.

Fetches current Spotify follower count and rewrites the animateCounter()
values in index.html. The GitHub Action commits and pushes the change,
and GitHub Pages auto-deploys.
"""

import logging
import os
import re
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ARTIST_ID: str = os.getenv("SPOTIFY_ARTIST_ID", "02lo7GheOKHi4dcjFhh46B")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--html-path", default="index.html")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET")
        sys.exit(1)

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
    )

        try:
        artist = sp.artist(ARTIST_ID)
    except spotipy.SpotifyException as exc:
        logger.warning(
            "Spotify API unavailable (%s); keeping existing stats. "
            "Likely the app owner's Spotify Premium has lapsed "
            "(Feb 2026 Web API dev-mode requirement).",
            exc,
        )
        return
    except Exception as exc:  # network/transient
        logger.warning("Could not reach Spotify (%s); keeping existing stats.", exc)
        return

    followers = artist.get("followers", {}).get("total", 0)    logger.info("Spotify followers: %d", followers)

    stream_estimate = max(followers * 20, 1000)

    if not os.path.exists(args.html_path):
        logger.error("File not found: %s", args.html_path)
        sys.exit(1)

    with open(args.html_path, "r", encoding="utf-8") as f:
        html = f.read()

    spotify_val = max(followers, 50)
    html = re.sub(
        r"(animateCounter\('stat-spotify',\s*)\d+",
        rf"\g<1>{spotify_val}",
        html,
    )
    html = re.sub(
        r"(animateCounter\('stat-streams',\s*)\d+",
        rf"\g<1>{stream_estimate}",
        html,
    )

    if args.dry_run:
        logger.info("DRY RUN: stat-spotify=%d, stat-streams=%d", spotify_val, stream_estimate)
        return

    with open(args.html_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("Updated: stat-spotify=%d, stat-streams=%d", spotify_val, stream_estimate)


if __name__ == "__main__":
    main()
