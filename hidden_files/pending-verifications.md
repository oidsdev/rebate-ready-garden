# Pending verifications — brand account signups
Owner-approved: David granted inbox access for verification codes (2026-10-01).
Inbox: orbitdesk.ops@gmail.com. Codes are relayed, never stored here.

## Protocol (for Grok / team)
1. When a signup needs an email code, post in #desk-team: `CODE NEEDED: <service> (sent ~HH:MM ET)`
2. Muse (or the daily outreach worker) runs `check-verifications.sh` and relays the code via room DM/file — never as a plain room message.
3. Do signups when Muse is likely around (mornings ET); codes expire in 15-60 min.

## Credential handoff (OAuth app keys, etc.)
Use Oids file transfer (R2-backed), NOT room messages. Upload the JSON, then post `FILE READY: <name>` in #desk-team. Muse pulls it to `~/.config/rebate-garden/` with 0600.

## Log
| Date | Who | Service | Status |
|------|-----|---------|--------|
| 2026-10-01 | Grok | Reddit u/RebateReadyGarden signup | pending |
| 2026-10-01 | Grok | X @RebateReadyGarden | pending |
| 2026-10-01 | Grok | Facebook business Page | pending |
