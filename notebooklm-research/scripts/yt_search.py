#!/usr/bin/env python3
"""
YouTube search via yt-dlp for notebooklm-research skill.
Returns filtered video metadata as JSON.

Usage:
    python yt_search.py "<query>" [--count N] [--niche] [--min-duration-secs N]

Output: JSON list of {url, title, duration_seconds, view_count, age_days, has_captions, notebooklm_ready}
  - notebooklm_ready: False if video is <72 hours old (NotebookLM limitation), but video is still returned
  - Hard filters: no captions, duration too short
  - Pass --show-filtered to see what was hard-excluded
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

# Words appended to query in --niche mode to steer away from beginner explainers
# toward practitioners, researchers, and deep specialists
NICHE_BOOST_TERMS = "practitioner strategy deep dive advanced"


def search_youtube(query: str, count: int) -> list[dict]:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        "--flat-playlist",
        f"ytsearch{count}:{query}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"yt-dlp error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return videos


def get_video_details(url: str) -> dict | None:
    """Fetch full video metadata including captions and upload date."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return None


def compute_age_days(upload_date_str: str | None) -> int | None:
    """Convert yt-dlp upload_date (YYYYMMDD) to age in days."""
    if not upload_date_str:
        return None
    try:
        upload_date = datetime.strptime(upload_date_str, "%Y%m%d").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(timezone.utc)
        return (now - upload_date).days
    except ValueError:
        return None


def has_captions(video_data: dict) -> bool:
    subtitles = video_data.get("subtitles", {})
    auto_captions = video_data.get("automatic_captions", {})
    return bool(subtitles) or bool(auto_captions)


def main():
    parser = argparse.ArgumentParser(description="YouTube search for notebooklm-research")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--count", type=int, default=15, help="Number of results to fetch (pre-filter)")
    parser.add_argument("--niche", action="store_true", help="Append practitioner/deep-dive terms to steer away from beginner content")
    parser.add_argument("--min-duration-secs", type=int, default=300, help="Minimum duration in seconds (default: 300 = 5 min)")
    parser.add_argument("--max-results", type=int, default=5, help="Max results to return after filtering")
    parser.add_argument("--show-filtered", action="store_true", help="Also output hard-excluded videos with reason")
    args = parser.parse_args()

    search_query = f"{args.query} {NICHE_BOOST_TERMS}" if args.niche else args.query
    print(f"Searching YouTube: '{search_query}' (fetching {args.count} candidates)...", file=sys.stderr)

    search_results = search_youtube(search_query, args.count)
    if not search_results:
        print(json.dumps({"results": [], "filtered": [], "error": "No results from yt-dlp"}))
        return

    kept = []
    filtered = []

    for video in search_results:
        url = video.get("url") or video.get("webpage_url") or f"https://www.youtube.com/watch?v={video.get('id', '')}"
        title = video.get("title", "Unknown")

        # Fetch full details for caption check and accurate metadata
        details = get_video_details(url)
        if not details:
            filtered.append({"url": url, "title": title, "reason": "Could not fetch video details"})
            continue

        duration = details.get("duration", 0) or 0
        upload_date = details.get("upload_date")
        age_days = compute_age_days(upload_date)
        view_count = details.get("view_count", 0) or 0
        captions = has_captions(details)

        # Hard filters: these videos cannot be used at all
        if duration < args.min_duration_secs:
            filtered.append({"url": url, "title": title, "reason": f"Too short ({duration}s, need {args.min_duration_secs}+s)"})
            continue

        if not captions:
            filtered.append({"url": url, "title": title, "reason": "No captions available"})
            continue

        # Soft flag: <72 hours old means NotebookLM may fail to import transcript.
        # Still include the video — the skill will warn and attempt it anyway.
        notebooklm_ready = age_days is None or age_days >= 3

        kept.append({
            "url": url,
            "title": title,
            "duration_seconds": duration,
            "view_count": view_count,
            "age_days": age_days,
            "has_captions": captions,
            "notebooklm_ready": notebooklm_ready,
        })

        if len(kept) >= args.max_results:
            break

    output = {"results": kept}
    if args.show_filtered:
        output["filtered"] = filtered

    print(json.dumps(output, indent=2))

    not_ready = [v for v in kept if not v["notebooklm_ready"]]
    print(f"\nFound {len(kept)} usable videos ({len(not_ready)} may fail NotebookLM import — too recent), hard-excluded {len(filtered)}.", file=sys.stderr)


if __name__ == "__main__":
    main()
