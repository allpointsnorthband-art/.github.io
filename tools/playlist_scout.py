"""
Playlist Scout -- Find independent Spotify playlists to pitch to.

Searches Spotify for playlists matching progressive rock / metal keywords,
filters by follower count and recency, and outputs curator targets as CSV.

Usage:
    python playlist_scout.py
    python playlist_scout.py --query "post-metal atmospheric" --min-followers 100
    python playlist_scout.py --output playlists.csv
"""

import argparse
import csv
import logging
import os
import sys
from datetime import datetime, timezone
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

DEFAULT_QUERIES: list[str] = [
    "progressive rock",
    "progressive metal",
    "prog rock 2026",
    "post-metal atmospheric",
    "prog metal new",
    "progressive rock underground",
    "technical metal atmospheric",
]

EXCLUDED_OWNERS: set[str] = {"spotify", "Spotify"}


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


def search_playlists(
    sp: spotipy.Spotify,
    query: str,
    min_followers: int = 200,
    max_followers: int = 5000,
    limit: int = 50,
) -> list[dict]:
    """Search Spotify for playlists matching a query and filter by follower count."""
    results: list[dict] = []
    offset = 0
    batch_size = 50

    while offset < limit:
        fetch_count = min(batch_size, limit - offset)
        try:
            response = sp.search(
                q=query,
                type="playlist",
                limit=fetch_count,
                offset=offset,
            )
        except Exception as e:
            logger.warning("Search failed for query '%s' at offset %d: %s", query, offset, e)
            break

        playlists = response.get("playlists", {}).get("items", [])
        if not playlists:
            break

        for pl in playlists:
            if pl is None:
                continue

            owner_name = pl.get("owner", {}).get("display_name", "")
            if owner_name in EXCLUDED_OWNERS:
                continue

            playlist_id = pl.get("id")
            if not playlist_id:
                continue

            try:
                details = sp.playlist(playlist_id, fields="followers,tracks.total")
            except Exception:
                continue

            follower_count = details.get("followers", {}).get("total", 0)
            if follower_count < min_followers or follower_count > max_followers:
                continue

            track_count = details.get("tracks", {}).get("total", 0)
            if track_count < 10:
                continue

            results.append({
                "name": pl.get("name", ""),
                "url": pl.get("external_urls", {}).get("spotify", ""),
                "owner": owner_name,
                "owner_url": pl.get("owner", {}).get("external_urls", {}).get("spotify", ""),
                "followers": follower_count,
                "tracks": track_count,
                "description": (pl.get("description") or "")[:200],
                "query": query,
            })

        offset += fetch_count
        if len(playlists) < fetch_count:
            break

    return results


def deduplicate(playlists: list[dict]) -> list[dict]:
    """Remove duplicate playlists by URL."""
    seen: set[str] = set()
    unique: list[dict] = []
    for pl in playlists:
        url = pl["url"]
        if url not in seen:
            seen.add(url)
            unique.append(pl)
    return unique


def write_csv(playlists: list[dict], output_path: str) -> None:
    fieldnames = ["name", "owner", "followers", "tracks", "url", "owner_url", "description", "query"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(playlists)
    logger.info("Wrote %d playlists to %s", len(playlists), output_path)


def print_report(playlists: list[dict]) -> None:
    print(f"\n{'='*80}")
    print(f"  PLAYLIST SCOUT RESULTS -- {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"  Found {len(playlists)} playlists to pitch")
    print(f"{'='*80}\n")

    playlists_sorted = sorted(playlists, key=lambda x: x["followers"], reverse=True)

    for i, pl in enumerate(playlists_sorted, 1):
        print(f"  {i:3d}. {pl['name'][:50]}")
        print(f"       Owner: {pl['owner']} | Followers: {pl['followers']:,} | Tracks: {pl['tracks']}")
        print(f"       {pl['url']}")
        if pl["description"]:
            print(f"       \"{pl['description'][:100]}...\"")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Find Spotify playlists to pitch to")
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Single search query (overrides default multi-query search)",
    )
    parser.add_argument("--min-followers", type=int, default=200)
    parser.add_argument("--max-followers", type=int, default=5000)
    parser.add_argument("--limit", type=int, default=50, help="Max results per query")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    sp = get_spotify_client()

    queries = [args.query] if args.query else DEFAULT_QUERIES
    all_playlists: list[dict] = []

    for q in queries:
        logger.info("Searching: '%s'", q)
        results = search_playlists(
            sp,
            query=q,
            min_followers=args.min_followers,
            max_followers=args.max_followers,
            limit=args.limit,
        )
        logger.info("  Found %d matching playlists", len(results))
        all_playlists.extend(results)

    unique = deduplicate(all_playlists)
    logger.info("Total unique playlists: %d", len(unique))

    print_report(unique)

    output_path = args.output or f"playlist_scout_{datetime.now().strftime('%Y%m%d')}.csv"
    write_csv(unique, output_path)


if __name__ == "__main__":
    main()
