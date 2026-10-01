# Reddit Outreach — Daily Worker Spec

Brand account: u/RebateReadyGarden (fallback names if taken). Email: orbitdesk.ops@gmail.com.
Tool: `reddit.py` in this directory. Stdlib only. Forum rules live in
`~/workspace/rebate-garden/hidden_files/forum-kit.md` and are ENFORCED by
`reddit.py` (see `SUBREDDIT_RULES`). Read the forum kit before every run.

## 0. One-time setup (after the browser signup completes)

1. Logged in as the brand account, go to https://www.reddit.com/prefs/apps/
2. "Create another app" → type **script**, name `rebate-ready-garden`,
   redirect URI `http://localhost:8080` (unused, required field).
3. Copy the client ID (under the app name) and the client secret.
4. `mkdir -p ~/.config/rebate-garden && cp config.template.json ~/.config/rebate-garden/reddit.json`
5. Fill in `client_id`, `client_secret`, `username`, `password`, `user_agent`
   (replace the placeholder username in the user_agent string).
6. `chmod 600 ~/.config/rebate-garden/reddit.json`
7. Verify: `python3 reddit.py me` → prints the brand username. Nothing else.

The real config is NEVER committed. Only `config.template.json` lives in git.

## 1. Daily run procedure

Every run does exactly this, in order:

1. `python3 warmup.py --subs <today's subs> --limit 10 --comments 3`
   Read the output. Pick threads where a genuinely helpful answer exists.
   Skip anything controversial, political, or medical. Skip threads where the
   OP already got a correct, complete answer.
2. Draft the reply/post in a text file under `/tmp/` (never in the repo).
   The worker DRAFTS the text; `reddit.py` never auto-composes in v1.
3. Run the humanizer checklist (section 4) on the draft. Rewrite until it passes.
4. Check the per-subreddit rule in `forum-kit.md`. When in doubt: comments-only.
5. Dry run: `python3 reddit.py reply <thing_id> --text-file /tmp/draft.txt --subreddit <sub> --dry-run`
   (or `submit ... --dry-run`). Confirm the output looks right and no REFUSED error.
6. Real post: same command without `--dry-run`.
7. Confirm it landed in `actions.log` (`tail -3 actions.log`).

Hard daily caps: **3 comments/day during warm-up; 1 standalone post/day during
outreach; never more than 5 total write actions in a day.** Reddit's own
rate limits are handled by the tool (1 req / 2s, 429 backoff).

## 2. Phase A — Warm-up (first 7 days after account creation)

Goal: look like a real gardening person before the account ever mentions the site.
Reddit's 90/10 norm: a brand-new account dropping links gets auto-removed.

- Subs: `r/NativePlantGardening`, `r/gardening`, `r/NoLawns` ONLY.
  Do NOT touch `r/nova`, `r/washingtondc`, `r/Maryland` until warm-up is done.
- 2–3 genuine helpful comments per day. Answer the actual question asked.
- **NO links. NO site mention. NO brand talk.** Just be useful.
  (r/NoLawns never gets links, in any phase — its wiki bans all self-promotion.)
- Good warm-up answers: plant ID help, "that looks like transplant shock, water
  deeply and mulch", native alternatives to a plant someone is removing, etc.
- Bad warm-up answers: anything that needs the site to answer, anything salesy.

Warm-up ends when: 7 days have passed AND the account has ~15+ genuine comments
AND no removals. Then Phase B begins.

## 3. Phase B — Outreach (after warm-up)

Follow `forum-kit.md` exactly. The awareness framing is the owner's call:

1. Hook: "did you know [place] pays $X for [practice]?"
2. Proof: the free database link (https://rebatereadygarden.com/rebate-database.html).
3. Footnote: plain disclosure + the $19.50 plans in ONE line.
4. Question: end with a genuine question (approval timing, inspection strictness,
   waitlist). Posts that ask something get replies; replies keep the thread alive.

Rules, all enforced by the tool unless noted:

- **One post per community, ever.** `posted.json` enforces this; `submit`
  refuses if the subreddit is already on record. Replies to comments on your
  own posts are fine and encouraged (reply to every comment on launch posts).
- **One community per day, max.** Space posts out; vary wording between drafts.
- **Every mention carries plain disclosure**: "I built this" / "it's my site".
  Never astroturf, never seed fake questions, never hype with a second account.
- **Subreddit standing orders** (also enforced in `SUBREDDIT_RULES`):
  - r/NoLawns — never post about the site, never link it. Comments stay
    purely helpful, forever.
  - r/NativePlantGardening — comments-only until the sidebar rules are read
    from a logged-in account and explicitly allow resource links. No links before.
  - r/nova, r/washingtondc, r/Maryland — comments-only. Mention the free
    database only when someone directly asks about rebates, with disclosure.
    Standalone promo posts get removed and burn the account.
  - Any community whose rules you haven't read: message the mods first.
    A two-line modmail beats a ban.
- Fairfax/NoVA draft stays on HOLD until the Fairfax locality page is live
  on the site.
- Each new daily location launch = one fresh "did you know?" post for that
  area, following the forum-kit's pairing template.

## 4. Humanizer checklist (every draft, no exceptions)

From the owner's standing rule. Read the draft aloud in your head:

- If it sounds like a press release, a blog intro, or a LinkedIn post, rewrite it.
- Kill AI tells: em-dashes as sentence glue; "delve," "tapestry," "landscape"
  (metaphorical), "game-changer," "unlock/unleash/elevate"; "It's not X, it's Y";
  "Here's the thing"; "Let's dive in"; triple parallel clauses
  ("fast, fearless, and free"); "In today's fast-paced world"; stacked rhetorical
  questions; an emoji at the end of every line; "vibrant/thriving/bustling."
- Vary sentence length. Short sentences are fine. Occasional fragments are fine.
- One idea per post. Cut throat-clearing openers — start with the thing itself.
- Numbers and specifics beat adjectives.
- Exclamation points: max one per draft, usually zero.
- Final test: would a tired human actually type this? If not, rewrite until yes.
- No fake reviews, no testimonials, no claims you can't verify. Rates come from
  the forum kit (official program pages as of Oct 2026).

## 5. Kill conditions (stop rules — not suggestions)

- **Mod removal or ban in a subreddit** → that subreddit is done, permanently.
  Run: `python3 -c "from reddit import record_banned; record_banned('<sub>', '<reason>')"`
  and report it to the owner. The tool refuses all future actions there.
- **429 rate limit** → the tool backs off automatically (up to 3 retries, then
  stops the run). Do NOT work around it, do NOT switch endpoints, do NOT retry
  manually the same day. Resume tomorrow.
- **REFUSED by rule check** → do not reword to sneak around it. The rule is the rule.
- **Account warning / shadowban signs** (comments not appearing when logged out,
  "you're doing that too much") → stop all activity, report to the owner.
- **Anything that feels like spam** → it is spam. Stop.

## 6. Logging and audit

- Every real action appends to `actions.log`: timestamp, action, target, excerpt.
  Passwords and tokens are NEVER logged (usernames and subreddits only).
- `posted.json` tracks launch posts per subreddit and banned subreddits.
- Before each run, `tail -5 actions.log` to confirm yesterday's state.
- Weekly: review `actions.log` for the owner — what was posted, where, and
  whether any threads need replies.

## 7. What the tool does NOT do

- No auto-composing of comment text (v1). The worker drafts; the tool posts.
- No DMs, no modmail automation, no voting, no following.
- No posting from the owner's personal accounts. Brand account only.
- No X posting — product promos there need the owner's explicit per-post approval.
