#!/usr/bin/env python3
"""
reddit.py — Reddit API client for the Rebate-Ready Garden brand outreach.

Stdlib only (urllib), no PRAW. OAuth2 script-app password grant:
  POST https://www.reddit.com/api/v1/access_token
  then https://oauth.reddit.com for everything else.

Config: ~/.config/rebate-garden/reddit.json (mode 0600) with
  client_id, client_secret, username, password, user_agent.

Subreddit rules from forum-kit.md (2026-10-01) are ENFORCED by this tool:
  - r/NoLawns: no submissions about the site, no links in replies. Ever.
  - r/NativePlantGardening: comments-only until sidebar rules are verified;
    no links in replies until then.
  - r/nova, r/washingtondc, r/Maryland: comments-only; links only with a
    printed warning (worker judgment: mention the free database only when
    directly relevant, with plain disclosure).
One-post-per-community-ever is enforced via posted.json.

Rate limit: max 1 request per 2 seconds. 429s honored with backoff; repeated
429s stop the run. Every real action appends to actions.log (timestamp,
action, target, excerpt). Passwords and tokens are NEVER logged.

Usage:
  reddit.py get-posts SUBREDDIT [--sort new] [--limit 25] [--json] [--config PATH]
  reddit.py get-comments SUBMISSION_ID [--limit 25] [--json] [--config PATH]
  reddit.py reply THING_ID --text-file PATH [--subreddit SUB] [--dry-run] [--config PATH]
  reddit.py submit SUBREDDIT --title TITLE --text-file PATH [--dry-run] [--config PATH]
  reddit.py me [--config PATH]
(Flags go after the subcommand.)
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

CONFIG_PATH = os.path.expanduser("~/.config/rebate-garden/reddit.json")
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"
MIN_INTERVAL = 2.0          # max 1 request per 2 seconds
MAX_RETRIES_429 = 3         # then stop

WORKDIR = os.path.dirname(os.path.abspath(__file__))
ACTIONS_LOG = os.path.join(WORKDIR, "actions.log")
POSTED_STATE = os.path.join(WORKDIR, "posted.json")
SITE_HOST = "rebatereadygarden.com"


# ---------------------------------------------------------------------------
# Subreddit rules, from ~/workspace/rebate-garden/hidden_files/forum-kit.md
# allow_submit=False  -> submit() refuses, always
# allow_links=False   -> reply() refuses when text contains a link
# allow_links="warn"  -> reply() prints a warning but proceeds (worker judgment)
# ---------------------------------------------------------------------------
SUBREDDIT_RULES = {
    "nolawns": {
        "allow_submit": False,
        "allow_links": False,
        "reason": "r/NoLawns wiki bans all self-promotion, including links to a company site",
    },
    "nativeplantgardening": {
        "allow_submit": False,
        "allow_links": False,
        "reason": "comments-only until the sidebar rules are read from a logged-in account",
    },
    "nova": {
        "allow_submit": False,
        "allow_links": "warn",
        "reason": "comments-only; standalone promo gets removed. Mention the free database "
                  "only when someone asks about rebates, with disclosure.",
    },
    "washingtondc": {
        "allow_submit": False,
        "allow_links": "warn",
        "reason": "comments-only; standalone promo gets removed. Mention the free database "
                  "only when someone asks about rebates, with disclosure.",
    },
    "maryland": {
        "allow_submit": False,
        "allow_links": "warn",
        "reason": "comments-only; standalone promo gets removed. Mention the free database "
                  "only when someone asks about rebates, with disclosure.",
    },
    "gardening": {
        "allow_submit": True,
        "allow_links": "warn",
        "reason": "warm-up subreddit. No links, no site mention during warm-up phase.",
    },
}


class RedditError(Exception):
    pass


class AuthError(RedditError):
    pass


class RateLimitedError(RedditError):
    pass


class RuleViolation(RedditError):
    pass


class AlreadyPostedError(RedditError):
    pass


class BannedSubredditError(RedditError):
    pass


def canon_sub(subreddit):
    """Normalize 'r/gardening' / 'Gardening' -> 'gardening'."""
    s = subreddit.strip().lower()
    if s.startswith("r/"):
        s = s[2:]
    return s


def has_link(text):
    t = text.lower()
    return SITE_HOST in t or "http://" in t or "https://" in t


def rule_for(subreddit):
    return SUBREDDIT_RULES.get(canon_sub(subreddit), {"allow_submit": True,
                                                      "allow_links": "warn",
                                                      "reason": "no specific rule on file; default to comments-first caution"})


def check_submit_allowed(subreddit):
    sub = canon_sub(subreddit)
    if sub in banned_subreddits():
        raise BannedSubredditError("r/%s is on the banned list (mod removal/ban recorded). "
                                   "Stop. Do not post there again." % sub)
    if sub in posted_subreddits():
        raise AlreadyPostedError("r/%s already has a launch post on record (posted.json). "
                                 "One post per community, ever." % sub)
    rule = rule_for(sub)
    if not rule["allow_submit"]:
        raise RuleViolation("submit to r/%s refused: %s" % (sub, rule["reason"]))


def check_reply_allowed(subreddit, text):
    sub = canon_sub(subreddit)
    if sub in banned_subreddits():
        raise BannedSubredditError("r/%s is on the banned list (mod removal/ban recorded). "
                                   "Stop. Do not post there again." % sub)
    rule = rule_for(sub)
    if has_link(text):
        if rule["allow_links"] is False:
            raise RuleViolation("reply to r/%s refused: text contains a link. %s" % (sub, rule["reason"]))
        if rule["allow_links"] == "warn":
            print("WARNING: reply to r/%s contains a link. %s" % (sub, rule["reason"]), file=sys.stderr)


# ---------------------------------------------------------------------------
# State: posted.json tracks one-post-per-community-ever and banned subs
# ---------------------------------------------------------------------------
def _load_state():
    if not os.path.exists(POSTED_STATE):
        return {"posted": {}, "banned": []}
    with open(POSTED_STATE) as f:
        return json.load(f)


def _save_state(state):
    tmp = POSTED_STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, POSTED_STATE)


def posted_subreddits():
    return _load_state().get("posted", {})


def banned_subreddits():
    return _load_state().get("banned", [])


def record_posted(subreddit):
    state = _load_state()
    state.setdefault("posted", {})[canon_sub(subreddit)] = \
        datetime.now(timezone.utc).isoformat()
    _save_state(state)


def record_banned(subreddit, reason=""):
    state = _load_state()
    banned = state.setdefault("banned", [])
    if canon_sub(subreddit) not in banned:
        banned.append(canon_sub(subreddit))
    _save_state(state)
    print("r/%s added to banned list. Reason: %s" % (canon_sub(subreddit), reason),
          file=sys.stderr)


# ---------------------------------------------------------------------------
# Logging: actions.log gets timestamp, action, target, excerpt. NEVER secrets.
# ---------------------------------------------------------------------------
def log_action(action, target, excerpt):
    line = "%s | %s | %s | %s\n" % (
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        action, target,
        excerpt.replace("\n", " ").replace("\r", " ")[:120],
    )
    with open(ACTIONS_LOG, "a") as f:
        f.write(line)


# ---------------------------------------------------------------------------
# Config + OAuth
# ---------------------------------------------------------------------------
def load_config(path=CONFIG_PATH):
    if not os.path.exists(path):
        raise AuthError(
            "config not found at %s\n"
            "  1. Copy reddit/config.template.json to %s\n"
            "  2. Register a script app at https://www.reddit.com/prefs/apps/\n"
            "     (logged in as the brand account) and fill in client_id/client_secret.\n"
            "  3. chmod 600 the config file." % (path, path))
    st = os.stat(path)
    if st.st_mode & 0o077:
        print("WARNING: %s is readable by others; run: chmod 600 %s" % (path, path),
              file=sys.stderr)
    with open(path) as f:
        cfg = json.load(f)
    for field in ("client_id", "client_secret", "username", "password", "user_agent"):
        if not cfg.get(field) or str(cfg[field]).startswith("PASTE_"):
            raise AuthError("config field '%s' is missing or still a placeholder in %s"
                            % (field, path))
    return cfg


class Reddit:
    def __init__(self, cfg):
        self.cfg = cfg
        self.token = None
        self.token_expires = 0
        self._last_req = 0.0

    # -- low-level ---------------------------------------------------------
    def _pace(self):
        elapsed = time.monotonic() - self._last_req
        wait = MIN_INTERVAL - elapsed
        if wait > 0:
            time.sleep(wait)

    def _raw(self, url, data=None, headers=None, auth_basic=None):
        req = urllib.request.Request(url, data=data, headers=headers or {})
        if auth_basic:
            req.add_header("Authorization", "Basic " + auth_basic)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def _request(self, method, path, params=None, form=None):
        """Authenticated request against oauth.reddit.com with pacing + 429 handling."""
        self._ensure_token()
        url = API_BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = urllib.parse.urlencode(form).encode() if form else None
        headers = {
            "Authorization": "Bearer " + self.token,
            "User-Agent": self.cfg["user_agent"],
        }
        attempts = 0
        while True:
            self._pace()
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    status, rheaders, body = resp.status, dict(resp.headers), resp.read()
            except urllib.error.HTTPError as e:
                status, rheaders, body = e.code, dict(e.headers), e.read()
            self._last_req = time.monotonic()

            if status == 429:
                attempts += 1
                if attempts > MAX_RETRIES_429:
                    raise RateLimitedError(
                        "429 rate-limited %d times in a row. Stopping per policy; "
                        "back off and resume later." % MAX_RETRIES_429)
                retry_after = int(rheaders.get("Retry-After", "60"))
                print("429 rate-limited; backing off %ds (attempt %d/%d)"
                      % (retry_after, attempts, MAX_RETRIES_429), file=sys.stderr)
                time.sleep(retry_after)
                continue

            # Proactive: Reddit tells us when the bucket is empty.
            remaining = rheaders.get("x-ratelimit-remaining")
            reset = rheaders.get("x-ratelimit-reset")
            if remaining is not None and reset is not None:
                try:
                    if float(remaining) < 1:
                        time.sleep(float(reset) + 1)
                except ValueError:
                    pass

            if status in (401, 403):
                # Token may have died early; refresh once and retry.
                self.token_expires = 0
                self._ensure_token()
                headers["Authorization"] = "Bearer " + self.token
                self._pace()
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        status, rheaders, body = resp.status, dict(resp.headers), resp.read()
                except urllib.error.HTTPError as e:
                    status, rheaders, body = e.code, dict(e.headers), e.read()
                self._last_req = time.monotonic()
                if status in (401, 403):
                    raise AuthError("request rejected (%d). Check account status / app credentials."
                                    % status)
            if status >= 400:
                raise RedditError("HTTP %d on %s %s: %s"
                                  % (status, method, path, body[:300].decode("utf8", "replace")))
            return json.loads(body.decode("utf8"))

    def _ensure_token(self):
        if self.token and time.time() < self.token_expires - 60:
            return
        basic = base64.b64encode(
            ("%s:%s" % (self.cfg["client_id"], self.cfg["client_secret"])).encode()
        ).decode()
        body = urllib.parse.urlencode({
            "grant_type": "password",
            "username": self.cfg["username"],
            "password": self.cfg["password"],   # used only here, never logged
        }).encode()
        status, _, raw = self._raw(
            TOKEN_URL, data=body,
            headers={"User-Agent": self.cfg["user_agent"],
                     "Content-Type": "application/x-www-form-urlencoded"},
            auth_basic=basic)
        if status != 200:
            raise AuthError("token request failed (HTTP %d). Check client_id/client_secret/username/password."
                            % status)
        tok = json.loads(raw.decode("utf8"))
        if "access_token" not in tok:
            raise AuthError("token response missing access_token: %s"
                            % raw[:200].decode("utf8", "replace"))
        # Token lives in memory only. Never written to disk or logs.
        self.token = tok["access_token"]
        self.token_expires = time.time() + int(tok.get("expires_in", 3600))

    # -- reads ---------------------------------------------------------------
    def me(self):
        return self._request("GET", "/api/v1/me")

    def get_posts(self, subreddit, sort="new", limit=25):
        sub = canon_sub(subreddit)
        data = self._request("GET", "/r/%s/%s.json" % (sub, sort),
                             params={"limit": max(1, min(limit, 100))})
        out = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            out.append({
                "id": d.get("id"),
                "fullname": d.get("name"),
                "title": d.get("title"),
                "author": d.get("author"),
                "score": d.get("score"),
                "num_comments": d.get("num_comments"),
                "created_utc": d.get("created_utc"),
                "permalink": d.get("permalink"),
                "selftext": (d.get("selftext") or "")[:500],
                "url": d.get("url"),
            })
        return out

    def get_comments(self, submission_id):
        sid = submission_id[3:] if submission_id.startswith("t3_") else submission_id
        data = self._request("GET", "/comments/%s.json" % sid, params={"limit": 50})
        if not isinstance(data, list) or len(data) < 2:
            return []
        out = []
        for child in data[1].get("data", {}).get("children", []):
            if child.get("kind") != "t1":
                continue
            d = child.get("data", {})
            replies = d.get("replies")
            n_replies = 0
            if isinstance(replies, dict):
                n_replies = len(replies.get("data", {}).get("children", []))
            out.append({
                "id": d.get("id"),
                "fullname": d.get("name"),
                "author": d.get("author"),
                "body": d.get("body") or "",
                "score": d.get("score"),
                "created_utc": d.get("created_utc"),
                "num_replies": n_replies,
            })
        return out

    # -- writes --------------------------------------------------------------
    def _check_write_errors(self, resp, what):
        errors = (((resp.get("json") or {}).get("errors")) or [])
        if errors:
            raise RedditError("%s rejected by Reddit: %s" % (what, "; ".join(
                "%s: %s" % (e[0], e[1]) for e in errors)))

    def reply(self, thing_id, text, dry_run=False):
        if not (thing_id.startswith("t1_") or thing_id.startswith("t3_")):
            raise RedditError("thing_id must be a fullname like t1_abc123 or t3_abc123")
        resp = self._request("POST", "/api/comment", form={
            "api_type": "json",
            "thing_id": thing_id,
            "text": text,
        })
        self._check_write_errors(resp, "reply")
        data = ((resp.get("json") or {}).get("data") or {}).get("things", [{}])[0].get("data", {})
        if dry_run:
            print("DRY-RUN reply -> %s" % thing_id)
            return {"dry_run": True}
        log_action("reply", thing_id, text)
        return {"id": data.get("id"), "fullname": data.get("name")}

    def submit(self, subreddit, title, text, dry_run=False):
        sub = canon_sub(subreddit)
        if dry_run:
            print("DRY-RUN submit -> r/%s" % sub)
            print("  title: %s" % title)
            return {"dry_run": True}
        resp = self._request("POST", "/api/submit", form={
            "api_type": "json",
            "sr": sub,
            "kind": "self",
            "title": title,
            "text": text,
        })
        self._check_write_errors(resp, "submit")
        data = ((resp.get("json") or {}).get("data") or {})
        record_posted(sub)
        log_action("submit", "r/" + sub, title)
        return {"fullname": data.get("name"), "url": data.get("url")}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _print_posts(posts):
    for p in posts:
        print("=" * 72)
        print("[%s] %s  (score %s, %s comments, u/%s)" % (
            p["fullname"], p["title"], p["score"], p["num_comments"], p["author"]))
        if p["selftext"]:
            print(p["selftext"][:300].replace("\n", " "))
        print("https://www.reddit.com" + (p["permalink"] or ""))


def _print_comments(comments):
    for c in comments:
        print("-" * 72)
        print("[%s] u/%s  (score %s, %s replies)" % (
            c["fullname"], c["author"], c["score"], c["num_replies"]))
        print(c["body"][:400])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reddit API client for Rebate-Ready Garden outreach")
    ap.add_argument("--dry-run", action="store_true",
                    help="print instead of posting (reply/submit only)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=CONFIG_PATH, help="path to reddit.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("get-posts", parents=[common],
                       help="list newest/hot/top posts in a subreddit")
    p.add_argument("subreddit")
    p.add_argument("--sort", default="new", choices=["new", "hot", "top", "rising"])
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("get-comments", parents=[common], help="list top-level comments on a submission")
    p.add_argument("submission_id", help="post id, e.g. abc123 or t3_abc123")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("reply", parents=[common], help="reply to a post or comment")
    p.add_argument("thing_id", help="fullname, e.g. t1_abc123 or t3_abc123")
    p.add_argument("--text-file", required=True, help="file containing the reply text")
    p.add_argument("--subreddit", default="",
                   help="subreddit the thread is in (enables forum-kit rule checks)")
    p.add_argument("--dry-run", action="store_true",
                   help="print instead of posting")

    p = sub.add_parser("submit", parents=[common], help="submit a self post to a subreddit")
    p.add_argument("subreddit")
    p.add_argument("--title", required=True)
    p.add_argument("--text-file", required=True, help="file containing the post body")
    p.add_argument("--dry-run", action="store_true",
                   help="print instead of posting")

    sub.add_parser("me", parents=[common], help="verify auth; print the logged-in username")

    args = ap.parse_args(argv)

    if args.cmd == "me":
        r = Reddit(load_config(args.config))
        print("logged in as u/%s" % r.me().get("name"))
        return 0

    if args.cmd == "get-posts":
        r = Reddit(load_config(args.config))
        posts = r.get_posts(args.subreddit, sort=args.sort, limit=args.limit)
        if args.json:
            print(json.dumps(posts, indent=2))
        else:
            _print_posts(posts)
        return 0

    if args.cmd == "get-comments":
        r = Reddit(load_config(args.config))
        comments = r.get_comments(args.submission_id)[:args.limit]
        if args.json:
            print(json.dumps(comments, indent=2))
        else:
            _print_comments(comments)
        return 0

    # write actions
    with open(args.text_file) as f:
        text = f.read().strip()
    if not text:
        print("error: text file is empty", file=sys.stderr)
        return 2

    if args.cmd == "reply":
        if not (args.thing_id.startswith("t1_") or args.thing_id.startswith("t3_")):
            print("error: thing_id must be a fullname like t1_abc123 or t3_abc123",
                  file=sys.stderr)
            return 2
        if args.subreddit:
            check_reply_allowed(args.subreddit, text)
        if args.dry_run:
            print("DRY-RUN reply -> %s" % args.thing_id)
            print(text)
            return 0
        r = Reddit(load_config(args.config))
        out = r.reply(args.thing_id, text)
        print("replied: %s" % out.get("fullname"))
        return 0

    if args.cmd == "submit":
        check_submit_allowed(args.subreddit)
        check_reply_allowed(args.subreddit, text)  # link caution applies to posts too
        if args.dry_run:
            print("DRY-RUN submit -> r/%s" % canon_sub(args.subreddit))
            print("  title: %s" % args.title)
            print(text)
            return 0
        r = Reddit(load_config(args.config))
        out = r.submit(args.subreddit, args.title, text)
        print("submitted: %s (%s)" % (out.get("fullname"), out.get("url")))
        return 0

    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuleViolation, AlreadyPostedError, BannedSubredditError) as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        sys.exit(3)
    except (AuthError, RateLimitedError, RedditError) as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)
