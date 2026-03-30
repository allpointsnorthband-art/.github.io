"""
Content Reposter -- Generate platform-specific posts from a single video.

Takes a Reel video file and generates:
- TikTok-ready version (re-encoded, no IG watermark)
- YouTube Shorts-ready version
- Platform-specific captions with hashtags

Usage:
    python content_reposter.py --input reel_sargassum.mp4 --track "Sargassum"
    python content_reposter.py --input reel_gear.mp4 --type gear --track "Embracer EP"

Requires: ffmpeg installed on system
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

CAPTION_TEMPLATES: dict[str, dict[str, str]] = {
    "performance": {
        "instagram": (
            "🎸 {track_name} -- riff breakdown.\n"
            "What's your favorite moment on Embracer?\n\n"
            "#allpointsnorth #embracer #progressiverock #progrock #progmetal "
            "#guitarriff #technicalmusic #dutchrock #newmusic2026 #livemusic"
        ),
        "tiktok": (
            "This riff from {track_name} 🔥 #progressiverock #progrock #progmetal "
            "#guitarriff #dutchrock #allpointsnorth #embracer #newmusic"
        ),
        "youtube": (
            "{track_name} -- All Points North (riff clip)\n\n"
            "From our EP \"Embracer\" (2026)\n"
            "Stream: https://open.spotify.com/artist/02lo7GheOKHi4dcjFhh46B\n\n"
            "#progressiverock #progrock #shorts"
        ),
    },
    "behind_the_scenes": {
        "instagram": (
            "Behind the music 🎶 Working on new material.\n"
            "The writing never stops.\n\n"
            "#allpointsnorth #embracer #progressiverock #bandlife #rehearsal "
            "#writingsession #behindthemusic #dutchrock #newmusic2026"
        ),
        "tiktok": (
            "Writing session vibes 🎵 #progressiverock #bandlife #rehearsal "
            "#writingsession #allpointsnorth #newmusic #progrock"
        ),
        "youtube": (
            "Writing session -- All Points North\n\n"
            "New material in the works.\n"
            "Stream \"Embracer\": https://open.spotify.com/artist/02lo7GheOKHi4dcjFhh46B\n\n"
            "#progressiverock #shorts #bandlife"
        ),
    },
    "gear": {
        "instagram": (
            "⚡ The tone behind {track_name}.\n"
            "What's your go-to setup?\n\n"
            "#allpointsnorth #embracer #progressiverock #guitartone #pedalboard "
            "#guitarrig #geartalk #dutchrock #progrock #progressivemetal"
        ),
        "tiktok": (
            "The tone behind {track_name} ⚡ #guitartone #pedalboard #guitarrig "
            "#progressiverock #allpointsnorth #geartalk #progrock"
        ),
        "youtube": (
            "Tone breakdown: {track_name} -- All Points North\n\n"
            "Stream \"Embracer\": https://open.spotify.com/artist/02lo7GheOKHi4dcjFhh46B\n\n"
            "#guitartone #progressiverock #shorts"
        ),
    },
}


def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def reencode_video(input_path: str, output_path: str, platform: str) -> bool:
    """Re-encode video for a specific platform."""
    codec_args = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
    ]

    if platform == "tiktok":
        codec_args.extend(["-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"])
    elif platform == "youtube":
        codec_args.extend(["-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"])

    codec_args.append(output_path)

    try:
        result = subprocess.run(codec_args, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("ffmpeg failed: %s", result.stderr[:500])
            return False
        return True
    except Exception as e:
        logger.error("ffmpeg execution error: %s", e)
        return False


def generate_captions(content_type: str, track_name: str) -> dict[str, str]:
    """Generate platform-specific captions from templates."""
    templates = CAPTION_TEMPLATES.get(content_type, CAPTION_TEMPLATES["performance"])
    return {
        platform: template.format(track_name=track_name)
        for platform, template in templates.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cross-platform video posts")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--track", default="Embracer", help="Track or content name")
    parser.add_argument(
        "--type",
        choices=["performance", "behind_the_scenes", "gear"],
        default="performance",
        help="Content type for caption generation",
    )
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--captions-only", action="store_true", help="Generate captions only, skip video re-encoding")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error("Input file not found: %s", args.input)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    captions = generate_captions(args.type, args.track)

    print(f"\n{'='*60}")
    print(f"  CONTENT REPOSTER -- {args.track}")
    print(f"{'='*60}")

    for platform, caption in captions.items():
        print(f"\n  [{platform.upper()}]")
        print(f"  {'─'*40}")
        print(f"  {caption}")

    caption_path = os.path.join(args.output_dir, f"captions_{args.track.lower().replace(' ', '_')}.json")
    with open(caption_path, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    logger.info("Captions saved to %s", caption_path)

    if args.captions_only:
        print(f"\n  Captions-only mode. Video re-encoding skipped.\n")
        return

    if not check_ffmpeg():
        logger.warning("ffmpeg not found. Install ffmpeg for video re-encoding.")
        logger.info("Captions generated successfully. Re-encode manually or install ffmpeg.")
        return

    base_name = os.path.splitext(os.path.basename(args.input))[0]

    for platform in ["tiktok", "youtube"]:
        output_path = os.path.join(args.output_dir, f"{base_name}_{platform}.mp4")
        logger.info("Encoding for %s: %s", platform, output_path)
        success = reencode_video(args.input, output_path, platform)
        if success:
            print(f"\n  [{platform.upper()}] Video: {output_path}")
        else:
            print(f"\n  [{platform.upper()}] Encoding failed -- check logs")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
