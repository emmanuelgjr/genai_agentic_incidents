# WS0-T3 — D11(b) row-level marker: schema shape

**Date:** 2026-07-27
**Author:** schema-architect (sole writer of `schema/`)
**Implements:** `docs/specs/WS0-T3-rescoped-2026-07-18.md` §6.1(i)/(ii); PROGRESS.md
decisions D9, D11, D12.
**Status:** shape decided; schema landed. Propagation, notice prose, and the
STIX/MISP CI assertion belong to pipeline-engineer (§4 of the rescoped spec) —
see §4 below for the exact handoff list.

---

## 1. The chosen shape

A dedicated, optional, **source-generic object field** on the incident record:

```
content_license: {
  source          (required)  slug of the source imposing the obligation
  license         (required)  SPDX identifier
  license_url     (optional)  canonical deed/legal-code URL
  attribution     (required)  human-readable party to credit
  attribution_url (optional)  URL to credit alongside it
  obligations     (required)  non-empty subset of ["attribution", "share-alike"]
}
```

`additionalProperties: false` on the object, matching the schema's existing
house style for structured fields (`references`, `maestro_layers`).

Plus a top-level conditional that makes §6.2's first acceptance criterion
**schema-enforced** rather than only jq-checked:

```json
"allOf": [
  {
    "if": {
      "required": ["description_source"],
      "properties": { "description_source": { "const": "aiaaic" } }
    },
    "then": { "required": ["content_license"] }
  }
]
```

## 2. Rationale

**Why a field and not a tag.** `tags` is the wrong carrier on three independent
counts, each verifiable in code today. It **unions across merges** rather than
staying sticky (`merge_into`, `merge_and_dedupe.py:1636-1691`), so a tag would
spread from an AIAAIC row to every entry that absorbed it — the exact opposite
of row-level containment. It is **truncated to the first 8 entries** in the slim
projection (`merge_and_dedupe.py`'s `slim` dict: `(e.get("tags") or [])[:8]`), so
the marker could be silently dropped from the most-redistributed artifact
precisely when a row is tag-rich. And a bare tag string cannot carry a machine-
readable license identity *and* an attribution target *and* the obligation set;
flattening those into one token invents a micro-format the schema cannot check.

**Why an object and not a bare string.** CC BY-SA 4.0 §3(a) requires the
attribution target and a link to the license, not merely the license's name. A
consumer holding only `data/incidents.min.json` — which after D12(a) is a
carrier of this marker, and which is also what ships inside the pip package via
`render_markdown.py:755` — may have no other license surface in hand. The object
makes that row self-sufficient.

**Why `obligations` is explicit rather than derived from `license`.** The
rescoped spec §6.4 records a concrete, near-term possibility: an AIAAIC reply, or
a waiver, could downgrade this from a ShareAlike-implying notice to an
attribution-only one. With obligations stated explicitly, that downgrade is a
**value** change (drop `"share-alike"`) on the existing shape. If obligations
were inferred from the SPDX identifier there would be no honest way to express
"CC-BY-SA-4.0 content, share-alike waived by the licensor" — no SPDX identifier
means that — and the downgrade would force a shape change instead.

**Why the field name carries no source.** §6.1(i) requires source-generic naming:
the source lives in the `source` **value**, so a future source with row-level
obligations reuses the mechanism unchanged. The *conditional* in §1 is
deliberately AIAAIC-keyed, because the obligation itself is source-specific
today; its `$comment` instructs the next editor to extend it per source rather
than delete it, mirroring §6.2's "re-scoped per-source, not dropped."

**Why `source` duplicates information also in `description_source`.** It does not
duplicate it where it matters. `description_source` is not carried in
`incidents.min.json` at all, so a min.json consumer would otherwise see an
obligation with no machine-readable statement of whose it is. It also gives
assertions a stable slug to key on instead of the display prose in
`attribution`.

## 3. Example of a marked row

Full record (`data/incidents.json`, and the HuggingFace export, which is a flat
projection of it):

```json
{
  "id": "INC-0XXXX",
  "title": "…",
  "description": "AIAAIC-tracked incident. System: … Technology: … Sector: … Jurisdiction: …",
  "description_provenance": "original",
  "description_source": "aiaaic",
  "content_license": {
    "source": "aiaaic",
    "license": "CC-BY-SA-4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution": "AIAAIC Repository",
    "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
    "obligations": ["attribution", "share-alike"]
  },
  "…": "…"
}
```

Slim projection (`data/incidents.min.json`) — the marker is the **only** added
key, present on marked rows and **absent** on every other row; the object is
carried whole, not re-shaped, so there is exactly one marker format across
surfaces:

```json
{
  "id": "INC-0XXXX",
  "title": "…",
  "description": "AIAAIC-tracked incident. System: …",
  "…": "…",
  "content_license": {
    "source": "aiaaic",
    "license": "CC-BY-SA-4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution": "AIAAIC Repository",
    "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
    "obligations": ["attribution", "share-alike"]
  }
}
```

The literal `attribution` / `attribution_url` / `license_url` values above are
the shape's expectation, not a licensing ruling; pipeline-engineer should
confirm the attribution string and repository URL against the live AIAAIC
footer at implementation time, and license-auditor owns any change to what the
obligation set should say.

## 4. Handoff to pipeline-engineer

1. **Ingest set-point.** Set `content_license` at the same place and time as
   `description_source == "aiaaic"` in `ingest_aiaaic_sheet.py` — one code path,
   so the two can never disagree. The schema conditional now fails the build if
   they do.
2. **`merge_into` exclusion.** `content_license` must **not** be added to
   `merge_into`'s union/absorb behaviour (`merge_and_dedupe.py:1636-1691`), for
   the same reason `description_source` is excluded: stickiness to the dedup
   target is what makes the marker truthful.
   Separately, and easy to conflate: `_CONTENT_FIELDS`
   (`merge_and_dedupe.py:1006`) is **not** the merge list — it is the snapshot
   that decides when `updated` bumps (invariant 4). Recommendation: **leave
   `content_license` out of it.** Including it changes nothing in this build
   (`description` is already in that tuple, so every marked row's `updated`
   bumps from the D9 rewrite anyway), but it would later make a pure licensing
   correction — an AIAAIC waiver downgrading `obligations`, per §6.4 — present
   itself as a change to the incident's content. pipeline-engineer/foreman own
   the final call; this is the shape owner's reasoning, not a ruling.
3. **min.json conditional carry (D12(a)).** In the `slim` dict
   (`merge_and_dedupe.py:1590-1613`), add the key **only when present** on the
   source entry — not `e.get("content_license")`, which would emit `null` on
   every unmarked row and defeat "slim otherwise". min.json has **no schema and
   no validator** (`schema/` holds only `incident.schema.json`; the slim shape
   is code-only), so this requirement is the only specification of it — hence
   its being written here. Note that the same bytes are copied into the pip
   package and the site (`render_markdown.py:751-755`), so this reaches the
   package automatically.
4. **HuggingFace export.** No code change needed — `export_huggingface.py:11-13`
   is a flat projection of the full record. The dataset-card prose is separate
   and is requirement §6.1(iii).
5. **STIX/MISP (D12(b)).** No marker. Add the CI assertion that these exports
   contain zero AIAAIC-derived rows, so the condition is checked rather than
   assumed.
6. **Notice-surface prose** (`NOTICE-DATA`, `.reuse/dep5`, README, and the
   `.zenodo.json` check D12(c) routed to implementation) is pipeline-engineer's
   per spec §4 — not touched here.
7. **Documentation debt this PR does not discharge:** `docs/DATA_DICTIONARY.md`
   documents neither `content_license` nor, as of today, the two D9 fields
   `description_provenance` / `description_source` — those shipped to schema
   only at `a2d7a26e`. All three need dictionary entries. This is flagged, not
   fixed, because this branch is scoped to `schema/` alone; it should land with
   the implementation PR that touches the other doc surfaces anyway.

## 5. Verification recipe

Files changed: `schema/incident.schema.json` and its packaged copy
`src/genai_incidents/schema/incident.schema.json`, kept byte-identical. The
packaged copy is regenerated from the canonical one by
`render_markdown.py:767`, so the two stay in sync on the next build regardless.


```
python -m pytest -q                 # full suite
python scripts/validate.py          # schema + cross-entry integrity gates
```

`validate.py` loads `schema/incident.schema.json` at runtime
(`validate.py:124`), so the new field and its conditional are enforced with no
change to the validator. Because the root schema sets
`additionalProperties: false`, the field addition is **load-bearing rather than
merely descriptive**: without it, a marker written by the pipeline would fail
validation outright.

Both commands were green on this branch at the (dated, approximate) corpus size
of roughly thirteen thousand entries as of 2026-07-27, with the conditional
passing vacuously — no entry carries `description_source` yet, since the D9
rebuild was reverted and only its schema fields were kept. The conditional
becomes binding the moment pipeline-engineer's rebuild sets that field, which is
the intent.

Direct check of the conditional, independent of the corpus:

```
python - <<'PY'
import json, jsonschema
v = jsonschema.Draft202012Validator(
    json.load(open('schema/incident.schema.json', encoding='utf-8')))
base = {'id':'INC-00001','title':'Test entry title','date':'2025-01-01','year':2025,
        'category':'real-world','description':'x'*30,'severity':'Low',
        'references':[{'url':'https://example.org'}]}
print('marker missing on an aiaaic row ->',
      [e.message for e in v.iter_errors(dict(base, description_source='aiaaic'))])
PY
```

Expected: `["'content_license' is a required property"]`.
