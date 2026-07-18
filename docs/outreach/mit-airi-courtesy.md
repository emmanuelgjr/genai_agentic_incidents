# Draft — MIT AIRI Navigator courtesy notice + transitive-AIID question

**STATUS:** ✅ CLEARED TO SEND (2026-07-18) — claims re-verified: the ZIP returns
HTTP 404 / 0 bytes as of 2026-07-18; the gated-link point is hedged ("appears")
and board-established (E6); the transitive-AIID point is a question, not a claim.
User verifies recipient (Spencer Michaels / airi-navigator.com) and sends; log
send date on the board (E3 / WS0-T4).
**To (UNCONFIRMED):** Spencer Michaels — airi-navigator.com
**Suggested subject:** AIRI Navigator — public data download appears withdrawn + a licensing question

---

Hello Spencer,

I maintain **genai_incidents**, an open index of AI incidents, and we have been
ingesting the AIRI Navigator dataset. Two small things — one courtesy notice and
one question.

1. **Courtesy notice — the public download appears to be gone.** The bulk data
   download our pipeline used
   (`https://www.airi-navigator.com/downloads/airi-data.zip`) now returns
   **HTTP 404 / 0 bytes**, and the on-page download link appears gated behind a
   flag that evaluates false, so it is not reachable. If the public export was
   intentionally withdrawn, no problem at all — I wanted to flag it in case it
   is unintentional. Our automated ingest now fails on the missing download each
run; we have stopped relying on it and are deciding whether to retire or replace
it — and we are not scraping around the withdrawal.

2. **Question — transitive AIID licensing.** As I understand it, part of the
   AIRI Navigator dataset derives from the AI Incident Database, which is
   CC BY-SA 4.0. I want to make sure that any AIRI-derived records we retain
   carry the correct upstream attribution and terms. Could you confirm how the
   AIID-derived portion is licensed as redistributed through AIRI Navigator, and
   whether there is a sanctioned export/API channel you would recommend now that
   the public ZIP is unavailable?

No urgency on either point — mainly want to attribute correctly and stop relying
on a download that is no longer there.

Thank you,
[Maintainer name]
genai_incidents
