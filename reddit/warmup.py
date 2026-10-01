#!/usr/bin/env python3
"""
warmup.py — fetch newest posts + top comments from a subreddit list so the
daily outreach worker can pick threads to answer genuinely.

Warm-up phase rules (from forum-kit.md):
  - NO links, NO site mention. Just be a useful gardening voice.
  - 2-3 genuine helpful comments/day across the warm-up subs.
  - Skip r/nova, r/washingtondc, r/Maryland until the warm-up week is done.

Usage:
  warmup.py [--subs NativePlantGardening,gardening,NoLawns] [--limit 10] [--comments 3] [--json]
"""

import argparse
import json
import sys

from reddit import Reddit, load_config, rule_for, canon_sub

DEFAULT_SUBS = ["NativePlantGardening", "gardening", "NoLawns"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Warm-up thread scout for Reddit outreach")
    ap.add_argument("--subs", default=",".join(DEFAULT_SUBS),
                    help="comma-separated subreddits (no r/ prefix needed)")
    ap.add_argument("--limit", type=int, default=10, help="newest posts per subreddit")
    ap.add_argument("--comments", type=int, default=3, help="top comments shown per post")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)

    r = Reddit(load_config(args.config) if args.config else load_config())
    subs = [s.strip() for s in args.subs.split(",") if s.strip()]

    report = []
    for sub in subs:
        rule = rule_for(sub)
        try:
            posts = r.get_posts(sub, sort="new", limit=args.limit)
        except Exception as e:
            print("ERROR fetching r/%s: %s" % (canon_sub(sub), e), file=sys.stderr)
            continue
        entry = {"subreddit": canon_sub(sub), "rule_note": rule["reason"], "posts": []}
        for p in posts:
            try:
                comments = r.get_comments(p["id"])[:args.comments]
            except Exception as e:
                print("ERROR fetching comments for %s: %s" % (p["fullname"], e),
                      file=sys.stderr)
                comments = []
            entry["posts"].append({
                "fullname": p["fullname"],
                "title": p["title"],
                "author": p["author"],
                "score": p["score"],
                "num_comments": p["num_comments"],
                "selftext_excerpt": p["selftext"][:300],
                "permalink": "https://www.reddit.com" + (p["permalink"] or ""),
                "top_comments": [
                    {"fullname": c["fullname"], "author": c["author"],
                     "score": c["score"], "body": c["body"][:300]}
                    for c in comments
                ],
            })
        report.append(entry)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    for entry in report:
        print("\n" + "=" * 78)
        print("r/%s  --  rule: %s" % (entry["subreddit"], entry["rule_note"]))
        print("=" * 78)
        for p in entry["posts"]:
            print("\n[%s] %s" % (p["fullname"], p["title"]))
            print("    u/%s | score %s | %s comments | %s" % (
                p["author"], p["score"], p["num_comments"], p["permalink"]))
            if p["selftext_excerpt"]:
                print("    %s" % p["selftext_excerpt"].replace("\n", " "))
            for c in p["top_comments"]:
                print("    - [%s] u/%s (score %s): %s" % (
                    c["fullname"], c["author"], c["score"],
                    c["body"].replace("\n", " ")))
    print("\n" + "-" * 78)
    print("REMINDER: warm-up phase = NO links, NO site mention. Pick 2-3 threads,")
    print("write genuinely helpful replies, run each through the humanizer checklist")
    print("in CRON_SPEC.md, then post with: reddit.py reply <thing_id> --text-file <draft> --subreddit <sub>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
