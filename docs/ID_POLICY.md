# Incident ID policy — headroom and stability

> **STATUS: DRAFT — decision pending (E4).** This document presents two
> options for the ID-width question with a recommendation. The human lead
> decides in Phase 1 (`MASTER_IMPROVEMENT_PLAN.md` §WS3-T5); implementation
> lands in Phase 2 with the other breaking changes. The **Stability policy**
> section (§4) is not part of the decision — it restates rules the project
> already follows and is published as policy either way.
>
> Owner: schema-architect (WS3). Related: WS6-T8 (v3.0 migration guide),
> WS1-T2 (corpus split), WS6-T3 (STIX).

---

## 1. Current state (measured 2026-07-27, at `main` @ 66b973ca)

### 1.1 Format

Every published incident carries an ID of the form `INC-` followed by a
zero-padded decimal number. As of the measurement date all 13,115 live IDs
match `INC-#####` exactly — one format, no variants, no gaps in the pattern:

| Property | Value |
|---|---|
| Distinct ID patterns in `data/incidents.json` | 1 (`INC-#####`) |
| ID string length | 9 characters, all entries |
| Live entries | 13,115 (`data/stats.json` → `incident_count`) |
| Lowest number in use | `INC-00001` |
| Highest number in use | `INC-14600` |
| Duplicate IDs | 0 |

The format is minted in two places, both as a **minimum**-width format, not a
fixed-width one:

- `scripts/merge_and_dedupe.py:324` — `def slug_to_id(n): return f"INC-{n:05d}"`
- `scripts/parse_existing.py:110` — identical

Python's `:05d` pads to five digits but does not truncate: `slug_to_id(100000)`
returns `INC-100000`. **The allocator therefore does not break at 99,999 — it
silently starts emitting six-digit IDs.** The width cap is enforced only by the
JSON Schema (`schema/incident.schema.json:12`, `"pattern": "^INC-[0-9]{5}$"`),
which means the first ID past 99,999 fails validation in CI rather than
corrupting data. That is a good failure mode, but it is an unplanned one.

### 1.2 ID-space consumption, including burn

The allocator's high-water mark is computed over live IDs **and** every ID ever
recorded in `data/id_deprecations.json` (`merge_and_dedupe.py`, `_load_prev_state`),
so a number is never handed out twice. Consumption is therefore strictly
greater than the live entry count:

| Quantity | Count | Share of numbers issued |
|---|---:|---:|
| Numbers issued (high-water `INC-14600`) | 14,600 | 100.0% |
| Live entries | 13,115 | 89.8% |
| Deprecated (tombstoned) IDs | 992 | 6.8% |
| Numbers issued but recorded nowhere ("silent burn") | 493 | 3.4% |

Deprecations break down as 704 `out-of-scope` (`into: null` — a terminal
tombstone, `resolve_id()` returns `None`) and 288 `merged` (redirects to a
surviving entry). The 493 silent-burn numbers are the arithmetic remainder
(14,600 − 13,115 − 992 = 493) and are explained in §1.4.

**Roughly one in ten numbers issued does not correspond to a live entry.** Any
runway estimate must be made against numbers *issued*, not against corpus size.

### 1.3 Burn rate and runway

Numbers issued over time, read from git history of `data/incidents.json`:

| Date | Live entries | High-water | Note |
|---|---:|---:|---|
| 2026-05-12 | 578 | — | first commit; project is 76 days old |
| 2026-06-10 | 9,209 | 9,630 | |
| 2026-06-10 | 12,062 | 12,571 | v2.3.0 bulk backfill (+2,941 in one day) |
| 2026-07-02 | 12,770 | 14,215 | v2.5.0→v2.6.0 CVE/NVD expansion (+788) |
| 2026-07-12 | 12,986 | 14,458 | |
| 2026-07-18 | 13,025 | 14,497 | +39 |
| 2026-07-27 | 13,115 | 14,600 | +103 (weekly auto-refresh #97) |

85,399 numbers remain below the `[0-9]{5}` ceiling. Runway depends entirely on
which regime you believe:

| Regime | Rate | Runway | Ceiling hit |
|---|---:|---:|---|
| Project-lifetime average (2026-05-12 → today) | 192/day | 445 days | late 2027 |
| Bulk-inclusive (2026-06-10 → today) | 106/day | 2.2 years | late 2028 |
| Post-backfill mixed (2026-06-11 → today) | 44/day | 5.3 years | mid-2031 |
| Recent weekly drip only (2026-07-02 → today) | 15/day | 15.2 years | 2041 |

The honest reading: **the weekly refresh will never exhaust the space; bulk
source onboardings might.** A single ingest expansion has cost up to 2,941
numbers. The space absorbs roughly 29 more events of that size. The plan
contemplates further source onboarding (WS1, WS4) and the WS1-T1 corpus split,
so "a few more bulk events per year" is the realistic planning assumption —
which puts the ceiling somewhere between 2031 and 2041, not this decade's
early years, but also not comfortably beyond the project's expected life.

Note also that the deprecation file's own growth is modest: 979 → 992 entries
in the 2026-07-27 refresh (+13). The large deprecation blocks (500 on
2026-06-10, 404 on 2026-06-11) came from one-off scope cleanups, not from
routine operation.

### 1.4 Two measured defects this document surfaces

Neither blocks the decision; both belong in the Phase-2 implementation task
whichever option wins.

**(a) 9 published IDs have no redirect.** Numbers 522, 609, 951, 952, 955, 956,
957, 1355 and 1660 were published in the `v2.0.0` release, disappeared in
`v2.1.0`, and appear in neither `data/incidents.json` nor
`data/id_deprecations.json` today. `resolve_id("INC-00522")` returns `None`
rather than a successor or a documented tombstone. This is a live violation of
the "merged IDs redirect forever" rule the policy below states — the rule
predates the tombstone machinery, which landed 2026-05-16. Fix: append nine
records with an honest reason (`unrecorded-drop-v2.1.0`), pointing at a
successor where one can be identified and `into: null` where it cannot.

**(b) 484 numbers were issued but never published.** The remaining silent burn
never appeared in any committed `incidents.json`, so no citation can exist for
them and no redirect is owed. They are allocator slack: numbers consumed by
rows that were dropped later in the same build. Harmless, but it means issued
≈ live × 1.11 and the runway table must use issued, not live.

---

## 2. Option A — widen to 7 digits in the v3.0 break

`INC-04853` becomes `INC-0004853`. Numbers are preserved; only padding changes.
(The alternative — renumbering — is not on the table: it would destroy every
external citation and is inconsistent with §4.)

### What changes

| Surface | Change |
|---|---|
| `schema/incident.schema.json:12` | `^INC-[0-9]{5}$` → `^INC-[0-9]{7}$` |
| `src/genai_incidents/schema/incident.schema.json:12-13` | same pattern + "Stable 5-digit…" description |
| `scripts/merge_and_dedupe.py:324`, `scripts/parse_existing.py:110` | `{n:05d}` → `{n:07d}` |
| `data/incidents.json` (+ `.min.json`, `docs/data/`, package copy) | every `id` rewritten — 13,115 values |
| `data/id_deprecations.json` | every `from`/`into` rewritten **and** 14,107 old→new records appended (the plan's "complete map") |
| `docs/404.html:26` | `/\/incident\/(INC-\d{5})\.html$/i` → variable width |
| `docs/DATA_DICTIONARY.md:9`, `README.md:103` | `INC-#####` / "stable 5-digit ID" wording |
| `docs/incidents/*.md`, site shards | regenerated; every in-page anchor changes |
| STIX / TAXII export | see blast radius below |
| MISP export | attribute and event UUIDs, plus `incident-id` tags and comments |
| HF export | the `id` column of every row |

File *names* are unaffected: per-incident standalone pages were withdrawn (see
`docs/404.html`), and the corpus files are named by corpus, not by ID.

### Blast radius (the part that is easy to underestimate)

The STIX exporter derives object identity from the ID string:
`export_stix.py:39-40` computes `uuid.uuid5(NS, prefix + "|" + parts)` and
`export_stix.py:100` calls `_sid("x-genai-incident", iid)`. Re-padding the ID
therefore **rotates the UUID of every incident object** (13,115 objects) and
every `relationship` object referencing them. `export_misp.py:57,101` has the
same property for attribute and event UUIDs. To a TAXII or MISP consumer this
is not a rename — it is a full replacement of the collection, with no
machine-readable link from the old object to the new one unless the migration
guide supplies the mapping out of band. WS6-T3's "real relationship objects"
and WS6-T4's TAXII work would land on top of a one-time identity rotation.

`resolve_id()` (`src/genai_incidents/__init__.py:167`) already follows chains
over an opaque dict, so a 14,107-entry old→new map works without code change —
at the cost of growing `id_deprecations.json` roughly fifteen-fold (992 →
~15,100 records), which is shipped inside the pip package
(`src/genai_incidents/data/id_deprecations.json`) and loaded on first call.

### Risks

1. **Every stored literal breaks.** Anyone who saved `INC-04853` in a
   spreadsheet, a paper, an issue tracker or a database column now holds a
   string that matches no entry. `resolve_id()` fixes it for pip users; for
   everyone else the fix is "read the migration guide".
2. **The map must be provably complete**, covering all 14,107 recorded numbers
   including deprecated ones (a citation of a merged-away ID must survive two
   hops: old-padded → new-padded → canonical successor). Defect (a) above must
   be fixed first or nine IDs migrate into a dead end.
3. **It buys headroom the project may not need** (9,999,999) at the cost of a
   break that lands on 100% of consumers — including the ~90% of the space
   that is nowhere near the cap.
4. **It does not remove the need for parsing tolerance.** During and after the
   transition, consumers must accept that `INC-04853` and `INC-0004853` denote
   the same incident. That is exactly the commitment Option B asks for — so
   Option A is Option B *plus* a rewrite of every published identifier.

---

## 3. Option B — a written padding-agnostic-parsing commitment

Keep `INC-` + five-digit minimum padding. Publish a commitment that the digit
run is a **variable-width decimal number**, and that when the counter passes
99,999 IDs organically become six digits (`INC-100000`), then seven, and so on.

### Exact wording of the commitment (proposed policy text)

> **Incident IDs are `INC-` followed by a decimal number with no upper bound
> on digit count.** IDs issued to date are zero-padded to a minimum of five
> digits; that padding is presentational and is not part of the identifier's
> meaning. Consumers MUST treat an ID as an opaque string for equality and
> lookup, and MUST NOT assume a fixed length, a five-digit width, or that
> lexicographic order equals issue order. Consumers that need numeric order
> MUST parse the digit run as an integer. The project will not re-pad,
> re-number, or otherwise rewrite an ID that has been published.

### What consumers must do

- **Equality/lookup:** nothing. Compare the full string. `by_id()` and
  `resolve_id()` already do exactly this.
- **Regex:** replace `INC-\d{5}` with `INC-\d+`. In this repo that is exactly
  two places: `schema/incident.schema.json:12` (and its package copy) and
  `docs/404.html:26`.
- **Sorting:** sort by the parsed integer, or by `added`/`date`, not by string.
  Today string order and numeric order agree; past 99,999 they diverge
  (`INC-100000` sorts before `INC-99999`).
- **Fixed-width storage:** a `CHAR(9)` column will truncate a six-digit ID. Use
  a variable-width text column.

### How new IDs are issued past 99,999

No code change. `f"INC-{n:05d}"` emits `INC-100000` for n = 100000; the
high-water scan in `_load_prev_state` already parses `^INC-(\d+)$`. The
allocator, `by_id()`, `resolve_id()`, the exporters and the search UI are
already width-agnostic. **Option B's implementation cost is two regex literals,
a schema description string, and documentation.** No data file changes, no ID
rewrites, no UUID rotation.

### Risks

1. **Consumers who zero-pad-assume today get a surprise later** — but at the
   moment the corpus crosses 99,999, not at v3.0, and only for entries above
   that line. Old IDs never change. Failure is localized and late rather than
   universal and immediate.
2. **Sort-order breakage** past 99,999 for anyone sorting IDs as strings. This
   is real and worth stating loudly in the commitment; it is also the only
   functional regression the option carries.
3. **Cosmetic inconsistency** — the corpus would eventually contain a mix of
   5- and 6-digit IDs. Ugly in a table; harmless to machines.
4. **The commitment must be enforced, not just written.** If the schema keeps a
   fixed-width pattern, the promise is a lie the first time it is tested. The
   Phase-2 task must widen the pattern to `^INC-[0-9]{5,}$` and add a
   validate.py test that a six-digit ID passes.

---

## 4. Stability policy (not part of the decision — published either way)

These three rules hold under both options and are stated here as project
policy. They align with the always-active board invariants in `CLAUDE.md`
("never delete entries — status + tombstone instead" and "IDs/tombstones are
append-only") and with plan invariants 3 and 4.

1. **IDs are never reused.** A number issued to an entry is retired with that
   entry. The allocator computes its high-water mark over live entries *and*
   every ID recorded in `data/id_deprecations.json`, so a retired number can
   never be handed to a different incident, even if the original entry is
   removed from the corpus entirely.

2. **Tombstones are append-only.** A record in `data/id_deprecations.json` is
   never edited to change its meaning and never deleted. Corrections are made
   by appending, not by rewriting history. A tombstone with `into: null` is
   terminal: the ID was withdrawn (out of scope) and resolves to nothing, which
   is a different and more honest answer than "not found".

3. **Merged IDs redirect forever.** When two entries merge, the surviving entry
   keeps the lower-numbered ID and every absorbed ID gains a record pointing at
   the survivor. Those redirects are permanent and transitively resolvable:
   `resolve_id()` follows a chain of any length and terminates. A citation of
   any ID this project has ever published must always resolve to either the
   current canonical entry or an explicit withdrawal — never to silence.
   *(Current compliance: 9 known exceptions — see §1.4(a) — to be repaired in
   Phase 2.)*

---

## 5. Recommendation

**Adopt Option B: publish the padding-agnostic-parsing commitment, widen the
schema pattern to `^INC-[0-9]{5,}$`, and do not re-pad any published ID.**

The rationale in one line: Option A costs a universal break — 13,115 rewritten
identifiers, a 15,000-record migration map, and a rotation of every STIX and
MISP object UUID — and still requires consumers to accept that two differently
padded strings mean the same incident, which is the entirety of what Option B
asks for. Option A is Option B plus a rewrite. The runway measurement says the
cap is 5 to 15 years out at observed rates and is threatened only by bulk
onboarding events, not by the weekly refresh; that is enough headroom to make
paying a universal-break cost now the wrong trade. If the corpus does approach
99,999, the transition to six digits is already implemented in the allocator
and affects only newly issued IDs.

Two conditions attach to this recommendation:

- **Enforce the commitment in the schema.** `^INC-[0-9]{5}$` must become
  `^INC-[0-9]{5,}$` in both schema copies in the v3.0 break, with a validate.py
  test proving a six-digit ID passes and `INC-1234` (four digits) fails. A
  written promise contradicted by the validator is worse than no promise.
- **Monitor the burn.** Publish numbers-issued alongside entry count (a
  `high_water_id` key in `data/stats.json` is the cheap version) so the runway
  is a measured number in CI rather than a thing someone re-derives by hand in
  three years. Revisit this decision if issued IDs pass 50,000.

**If the lead prefers Option A anyway** — the defensible reason is
presentational: fixed width keeps lexicographic sort equal to issue order
forever and keeps dumb `\d{7}` regexes working. If so, v3.0 is the only
acceptable moment for it, defect §1.4(a) must be repaired before the map is
generated, and WS6-T8 must carry a worked STIX/MISP UUID-rotation example, not
just a JSON before/after.

### What the decision unblocks

The choice is a direct input to **WS6-T8** (`docs/MIGRATING_TO_V3.md`), whose
acceptance criterion is that it covers every breaking change in the v3.0.0-beta
diff: under Option A that guide needs an ID-mapping section, a `resolve_id()`
worked example, and a warning that STIX/MISP object identities rotate; under
Option B it needs a short "IDs are unchanged; stop assuming five digits"
section and a regex-fix note. It also determines the size and shape of the
Phase-2 ID task — under Option A a data migration with a 14,107-entry map, a
fixture-backed migration script in `scripts/migrations/`, and `resolve_id()`
tests over every historical ID; under Option B a two-line schema change plus
those same `resolve_id()` tests, which are owed regardless (WS3-T5's third
acceptance clause). Until it is decided, WS6-T8 cannot be drafted to
completion and the Phase-2 breaking-change set is not fully enumerable.

---

## 6. Verification recipe

Every number in §1 is reproducible from the repository at `main`:

```bash
# 1.1 format, count, high-water, duplicates
python -c "import json,re,collections; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; ids=[e['id'] for e in d]; print(len(ids), len(set(ids)), collections.Counter(re.sub(r'[0-9]','#',i) for i in ids), max(int(i[4:]) for i in ids))"

# 1.2 deprecations, reasons, silent burn
python -c "import json; dep=json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']; import collections; print(len(dep), collections.Counter(d['reason'] for d in dep), sum(1 for d in dep if not d.get('into')))"

# 1.3 high-water over history (one line per revision of the data file)
git log --format=%H -- data/incidents.json

# 1.4(a) the nine unrecorded drops
git show v2.0.0:data/incidents.json    # contains INC-00522 et al.
python -c "import json; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; print(any(e['id']=='INC-00522' for e in d))"   # False

# allocator overflow behaviour
python -c "print(f'INC-{100000:05d}')"   # INC-100000
```

Corpus totals quoted in this document are as of 2026-07-27 and are stated with
their measurement date rather than templated, because this file is a
point-in-time decision record and is not on the `stats_docs_lib.DOC_SURFACES`
list.
