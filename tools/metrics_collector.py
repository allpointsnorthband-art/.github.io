"""
Metrics Collector -- Pull Spotify data and print a weekly summary.

Collects artist metrics from Spotify (followers, top tracks, related artists)
and prints a formatted report. Can be run manually or via cron / GitHub Action.

Usage:
    python metrics_collector.py
    python metrics_collector.py --json  # Output as JSON for further processing
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

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
        logger.error("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def collect_artist_data(sp: spotipy.Spotify, artist_id: str) -> dict[str, Any]:
    """Collect all available artist data from Spotify Web API."""
    artist = sp.artist(artist_id)

    top_tracks_response = sp.artist_top_tracks(artist_id, country="NL")
    top_tracks = []
    for track in top_tracks_response.get("tracks", [])[:5]:
        top_tracks.append({
            "name": track.get("name", ""),
            "popularity": track.get("popularity", 0),
            "album": track.get("album", {}).get("name", ""),
            "preview_url": track.get("preview_url"),
        })

    related_response = sp.artist_related_artists(artist_id)
    related = []
    for rel in related_response.get("artists", [])[:10]:
        related.append({
            "name": rel.get("name", ""),
            "followers": rel.get("followers", {}).get("total", 0),
            "popularity": rel.get("popularity", 0),
            "genres": rel.get("genres", [])[:3],
        })

    albums_response = sp.artist_albums(artist_id, album_type="single,album", limit=10)
    releases = []
    for album in albums_response.get("items", []):
        releases.append({
            "name": album.get("name", ""),
            "type": album.get("album_type", ""),
            "release_date": album.get("release_date", ""),
            "total_tracks": album.get("total_tracks", 0),
        })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artist": {
            "name": artist.get("name", ""),
            "id": artist_id,
            "followers": artist.get("followers", {}).get("total", 0),
            "popularity": artist.get("popularity", 0),
            "genres": artist.get("genres", []),
            "url": artist.get("external_urls", {}).get("spotify", ""),
        },
        "top_tracks": top_tracks,
        "related_artists": related,
        "releases": releases,
    }


def collect_playlist_appearances(sp: spotipy.Spotify, artist_id: str) -> list[dict]:
    """Search for playlists that contain APN tracks (limited heuristic)."""
    artist = sp.artist(artist_id)
    artist_name = artist.get("name", "All Points North")

    playlists_found: list[dict] = []
    try:
        results = sp.search(q=f'"{artist_name}"', type="playlist", limit=20)
        for pl in results.get("playlists", {}).get("items", []):
            if pl is None:
                continue
            owner = pl.get("owner", {}).get("display_name", "")
            if owner.lower() in ("spotify", artist_name.lower()):
                continue
            playlists_found.append({
                "name": pl.get("name", ""),
                "owner": owner,
                "url": pl.get("external_urls", {}).get("spotify", ""),
            })
    except Exception as e:
        logger.warning("Playlist appearance search failed: %s", e)

    return playlists_found


def print_report(data: dict[str, Any], playlist_appearances: list[dict]) -> None:
    artist = data["artist"]
    ts = datetime.fromisoformat(data["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")

    print(f"\n{'='*70}")
    print(f"  APN WEEKLY METRICS REPORT")
    print(f"  Generated: {ts}")
    print(f"{'='*70}")

    print(f"\n  ARTIST OVERVIEW")
    print(f"  {'─'*40}")
    print(f"  Name:          {artist['name']}")
    print(f"  Spotify ID:    {artist['id']}")
    print(f"  Followers:     {artist['followers']:,}")
    print(f"  Popularity:    {artist['popularity']}/100")
    print(f"  Genres:        {', '.join(artist['genres']) if artist['genres'] else 'Not yet categorized'}")
    print(f"  URL:           {artist['url']}")

    note = (
        "  NOTE: Monthly listeners are not available via the Spotify Web API.\n"
        "        Check Spotify for Artists app manually, or use spotifyscraper.\n"
    )
    print(f"\n{note}")

    if data["top_tracks"]:
        print(f"  TOP TRACKS (by popularity)")
        print(f"  {'─'*40}")
        for i, track in enumerate(data["top_tracks"], 1):
            print(f"  {i}. {track['name']} (popularity: {track['popularity']}/100)")
    else:
        print("  No top tracks data available yet.")

    if data["releases"]:
        print(f"\n  RELEASES")
        print(f"  {'─'*40}")
        for rel in data["releases"]:
            print(f"  {rel['release_date']}  {rel['name']} ({rel['type']}, {rel['total_tracks']} tracks)")

    if playlist_appearances:
        print(f"\n  PLAYLIST APPEARANCES (found {len(playlist_appearances)})")
        print(f"  {'─'*40}")
        for pl in playlist_appearances[:10]:
            print(f"  - {pl['name']} (by {pl['owner']})")
            print(f"    {pl['url']}")
    else:
        print("\n  No external playlist appearances found yet.")

    if data["related_artists"]:
        print(f"\n  RELATED ARTISTS (algorithmic neighbors)")
        print(f"  {'─'*40}")
        for rel in data["related_artists"][:5]:
            genres = ", ".join(rel["genres"]) if rel["genres"] else "N/A"
            print(f"  - {rel['name']} ({rel['followers']:,} followers, genres: {genres})")

    print(f"\n{'='*70}\n")


def save_json(data: dict[str, Any], playlist_appearances: list[dict], output_path: str) -> None:
    combined = {**data, "playlist_appearances": playlist_appearances}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    logger.info("Saved JSON report to %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect APN metrics from Spotify")
    parser.add_argument("--json", action="store_true", help="Output as JSON file")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    sp = get_spotify_client()

    logger.info("Collecting artist data for %s...", ARTIST_ID)
    data = collect_artist_data(sp, ARTIST_ID)

    logger.info("Searching for playlist appearances...")
    playlist_appearances = collect_playlist_appearances(sp, ARTIST_ID)

    print_report(data, playlist_appearances)

    if args.json:
        output_path = args.output or f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
        save_json(data, playlist_appearances, output_path)


if __name__ == "__main__":
    main()
