# Draft — AIAAIC facts+link handling / attribution

**STATUS:** ⛔ HELD (2026-07-18) — DO NOT SEND YET. The reduction is *restored, not
implemented* (WS0-T3 re-scoped, awaiting review), so the body's "we have reduced
AIAAIC-derived entries to facts plus a link" is **currently false**. AIAAIC prose
still sits in `ingest/aiaaic_sheet_incidents.json` (D10). Release this hold and
switch the phrasing to accomplished tense only after WS0-T3 lands and the prose
audit reads 0. Then user verifies recipient and sends; log send date (E3/WS0-T4).
**To (UNCONFIRMED):** AIAAIC (Charlie Pownall / AIAAIC team)
**Suggested subject:** genai_incidents — respecting AIAAIC's CC BY-SA terms (facts + link)

---

Hello AIAAIC team,

I maintain **genai_incidents**, an open, machine-readable index of publicly
reported GenAI and agentic-AI incidents. A number of entries draw on the AIAAIC
Repository, and I want to be transparent about how we handle your content under
its CC BY-SA 4.0 licence.

**How we use AIAAIC data.** To keep our dataset under a single clean permissive
licence without importing a share-alike obligation onto the whole corpus, we
have reduced AIAAIC-derived entries to **facts plus a link**:

- We keep only categorical facts (system, technology, sector, jurisdiction) and
  a **link back to the AIAAIC record**.
- We **do not** carry AIAAIC's editorial prose (the purpose / ethical-issues /
  consequences / response narrative) — that original expression stays on your
  site, and readers are sent to you for it.

Our reasoning is that categorical facts are not themselves copyrightable, while
your editorial narrative is, so linking rather than reproducing respects the
share-alike terms.

**Two questions:**

1. **Attribution.** Is there a specific attribution string or credit format you
   would like us to display on AIAAIC-derived entries?

2. **Cadence / access.** Is our periodic use of the public AIAAIC sheet an
   acceptable access pattern, or is there a preferred channel/cadence you would
   rather we follow?

We are also separately reviewing whether the EU/UK *sui generis* database right
bears on extraction at our scale; if you have a view on that we would welcome it.

Thank you for the work you do cataloguing these incidents — it is a real public
service.

Best regards,
[Maintainer name]
genai_incidents
