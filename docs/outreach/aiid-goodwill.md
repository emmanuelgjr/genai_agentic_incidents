# Draft — AIID goodwill / attribution confirmation

**STATUS:** ⛔ HELD (2026-07-18) — DO NOT SEND until WS0-T4 resolves. The body claims
"We have stopped high-volume access… now consume AIID only via your official
weekly snapshot channel" — **currently false**: D1's scraper-disable was never
implemented (`Makefile:83` still calls `scrape_aiid.py`) and no snapshot swap
exists (WS0-T4 re-opened P0). Release this hold once WS0-T4 lands (scraper
disabled + snapshot swap live), then verify recipient and send; log send date.
**To (UNCONFIRMED):** AI Incident Database team — Responsible AI Collaborative
**Suggested subject:** genai_incidents — attribution & respectful use of AIID data

---

Hello AI Incident Database team,

I maintain **genai_incidents**, an open, machine-readable index that consolidates
publicly reported GenAI and agentic-AI security incidents and maps them to
frameworks (OWASP LLM/ASI, NIST AI RMF, MITRE ATLAS). A meaningful portion of
the real-world incidents in it originate from the AI Incident Database, and I
want to make sure we are using your work respectfully and crediting it
correctly.

Two things I wanted to share and one question:

1. **We have stopped high-volume access.** We disabled per-incident concurrent
   fetching and now consume AIID only via your official weekly snapshot channel,
   consistent with your Terms of Use.

2. **Per-incident attribution.** Every AIID-derived entry in our published
   surface now carries a "Cite this incident" line pointing to the AIID record
   (`incidentdatabase.ai/cite/<id>/`) rather than to us — the aggregate is cited
   as our dataset, but individual incidents are credited to their AIID source.

3. **Question — attribution terms.** We treat AIID content as CC BY-SA 4.0 and
   attribute accordingly, and we understand the `reports.text` field is excluded
   from that grant (we do not redistribute it verbatim). Could you confirm
   whether that reflects your current terms, and whether there is a preferred
   attribution string or citation format you would like downstream indexes like
   ours to use?

Happy to adjust anything that would make our use more clearly aligned with your
wishes. Thank you for maintaining such a valuable public resource.

Best regards,
[Maintainer name]
genai_incidents
