"""
Reddit Listener -- Monitor subreddits for pitching and engagement opportunities.

Scans r/progmetal, r/progrockmusic, r/listentothis, and r/SpotifyPlaylists
for posts where All Points North could contribute. Prints actionable
opportunities to the terminal or sends a notification.

Usage:
    python reddit_listener.py
    python reddit_listener.py --subreddits progmetal progrockmusic
    python reddit_listener.py --hours 48

Requires: pip install praw python-dotenv
Also requires a Reddit API app: https://www.reddit.com/prefs/apps/
Add to .env:
    REDDIT_CLIENT_ID=
    REDDIT_CLIENT_SECRET=
    REDDIT_USER_AGENT=APN-Listener/1.0
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    import praw
except ImportError:
    print("Install praw: pip install praw")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_SUBREDDITS: list[str] = [
    "progmetal",
    "progrockmusic",
    "listentothis",
    "SpotifyPlaylists",
    "WhereDoIStart",
]

OPPORTUNITY_KEYWORDS: list[str] = [
    "progressive rock",
    "prog rock",
    "prog metal",
    "progressive metal",
    "post-metal",
    "playlist",
    "recommend",
    "recommendation",
    "dutch",
    "netherlands",
    "nederland",
    "self-promotion",
    "new band",
    "new music",
    "unknown band",
    "underrated",
    "underground",
    "tool",
    "haken",
    "tesseract",
    "karnivool",
    "porcupine tree",
    "similar to",
]

PROMO_THREAD_PATTERNS: list[str] = [
    r"self[- ]?promot",
    r"weekly.*promot",
    r"share.*music",
    r"feedback.*thread",
    r"what.*listening",
    r"new.*release",
    r"recommend.*thread",
    r"playlist.*thread",
]


def get_reddit_client() -> praw.Reddit:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "APN-Listener/1.0 by AllPointsNorth")

    if not client_id or not client_secret:
        logger.error("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in .env")
        sys.exit(1)

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def is_opportunity(title: str, selftext: str) -> tuple[bool, list[str]]:
    """Check if a post represents an engagement or pitching opportunity."""
    combined = f"{title} {selftext}".lower()
    matched_keywords: list[str] = []

    for keyword in OPPORTUNITY_KEYWORDS:
        if keyword in combined:
            matched_keywords.append(keyword)

    return len(matched_keywords) > 0, matched_keywords


def is_promo_thread(title: str) -> bool:
    """Check if a post is a self-promotion or recommendation thread."""
    title_lower = title.lower()
    for pattern in PROMO_THREAD_PATTERNS:
        if re.search(pattern, title_lower):
            return True
    return False


def scan_subreddit(
    reddit: praw.Reddit,
    subreddit_name: str,
    hours: int = 72,
) -> list[dict]:
    """Scan a subreddit for recent opportunities."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    opportunities: list[dict] = []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=100):
            post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            if post_time < cutoff:
                continue

            title = post.title or ""
            selftext = post.selftext or ""

            is_opp, keywords = is_opportunity(title, selftext)
            promo = is_promo_thread(title)

            if is_opp or promo:
                opp_type = "PROMO THREAD" if promo else "KEYWORD MATCH"
                opportunities.append({
                    "subreddit": subreddit_name,
                    "type": opp_type,
                    "title": title[:120],
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "comments": post.num_comments,
                    "keywords": keywords,
                    "created": post_time.strftime("%Y-%m-%d %H:%M"),
                })

    except Exception as e:
        logger.warning("Failed to scan r/%s: %s", subreddit_name, e)

    return opportunities


def print_report(all_opportunities: list[dict]) -> None:
    promo = [o for o in all_opportunities if o["type"] == "PROMO THREAD"]
    keyword = [o for o in all_opportunities if o["type"] == "KEYWORD MATCH"]

    print(f"\n{'='*70}")
    print(f"  REDDIT OPPORTUNITY SCANNER")
    print(f"  Found {len(all_opportunities)} opportunities")
    print(f"{'='*70}")

    if promo:
        print(f"\n  SELF-PROMOTION / SHARE THREADS ({len(promo)} found)")
        print(f"  {'─'*50}")
        print("  These threads explicitly invite you to share music.\n")
        for o in sorted(promo, key=lambda x: x["score"], reverse=True):
            print(f"  r/{o['subreddit']} | {o['created']} | score: {o['score']}")
            print(f"  \"{o['title']}\"")
            print(f"  {o['url']}")
            print()

    if keyword:
        print(f"\n  ENGAGEMENT OPPORTUNITIES ({len(keyword)} found)")
        print(f"  {'─'*50}")
        print("  Posts matching genre/scene keywords. Engage genuinely first.\n")
        for o in sorted(keyword, key=lambda x: x["score"], reverse=True)[:20]:
            kw = ", ".join(o["keywords"][:3])
            print(f"  r/{o['subreddit']} | {o['created']} | score: {o['score']} | {o['comments']} comments")
            print(f"  \"{o['title']}\"")
            print(f"  Keywords: {kw}")
            print(f"  {o['url']}")
            print()

    if not all_opportunities:
        print("\n  No opportunities found in the scanned timeframe.")
        print("  Try increasing --hours or adding more subreddits.\n")

    print(f"{'='*70}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan Reddit for APN opportunities")
    parser.add_argument(
        "--subreddits",
        nargs="+",
        default=DEFAULT_SUBREDDITS,
        help="Subreddits to scan",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=72,
        help="Look back this many hours (default: 72)",
    )
    args = parser.parse_args()

    reddit = get_reddit_client()

    all_opportunities: list[dict] = []

    for sub in args.subreddits:
        logger.info("Scanning r/%s (last %d hours)...", sub, args.hours)
        opportunities = scan_subreddit(reddit, sub, hours=args.hours)
        logger.info("  Found %d opportunities", len(opportunities))
        all_opportunities.extend(opportunities)

    print_report(all_opportunities)


if __name__ == "__main__":
    main()
