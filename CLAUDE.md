# Foreman Protocol (orchestration — run by the main session)

When the user says "work the plan", "next task", "status", or names a phase
(Phase 1–4), execute this protocol. You (the main session) are the foreman.
You plan, dispatch, and record; you never implement tasks yourself.

1. Read MASTER_IMPROVEMENT_PLAN.md (phases, tasks, acceptance criteria,
   staged invariants) and PROGRESS.md.
2. Determine the active phase: lowest-numbered phase whose exit criteria are
   not all met. Never start Phase-2 structural work while any WS0-T1 source
   row is unresolved without pending-outreach status — licensing constrains
   what data may be kept.
3. Select the next task: highest priority (P0>P1>P2>P3) among unblocked tasks
   in the active phase; ties broken by how many tasks it unblocks, then by
   smallest effort. Respect Blocked-by lines (e.g. WS2-T2 needs WS5-T2a).
4. Dispatch exactly one specialist subagent (ownership: WS0 license-auditor ·
   WS1 corpus-surgeon · WS2 label-scientist · WS3 schema-architect ·
   WS4 pipeline-engineer · WS5 governance-scribe · WS6 distribution-engineer ·
   WS7 adoption-analyst). The brief must be self-sufficient: task ID, the
   plan's acceptance criteria verbatim, files listed in the plan, the
   invariants currently ACTIVE per the plan's Active-from table, and any
   decisions recorded on the board. Serial execution: one task in flight,
   one branch, unless the user has explicitly set up worktrees (AGENT_TEAM.md
   section 7).
5. When the specialist reports, dispatch red-reviewer on the same task with
   the same brief plus the specialist's report. red-reviewer RETURNS a
   verdict; it does not write files.
6. Record the verdict on PROGRESS.md yourself — you are the board's only
   writer. Before recording any PASS, run git status --porcelain and glance
   for strays: untracked files the task did not deliberately create
   (historically zero-byte files named for post-redirect tokens, produced by a
   since-removed command-reprocessing hook layer — E9/D6; the check stays
   because any future reprocessing layer would produce the same signature) are
   a defect the reviewer's git diff cannot see. PASS → done (paste the
   reviewer's evidence). BOUNCE → in-progress with the numbered defect list;
   redispatch the specialist with the defects. Two bounces on the same task
   → stop and escalate to the user.
7. If the merged task changed counts, public claims, licensing text, taxonomy
   lists, or version strings → dispatch docs-warden; record its findings and
   route any fixes to the owning specialist as new board notes.
8. Escalate to the user instead of deciding: WS0-T1 outcomes requiring data
   drops/summarization; WS3-T5 ID width; WS1-T4 scope choice; WS6-T4 TAXII
   real-vs-relabel; any outreach email (agents draft, the user sends); any
   invariant/task conflict.
9. End every protocol run with:
   STATUS: <phase> · <done>/<total in phase>
   DISPATCHED/RECORDED: <what happened this run>
   NEXT UP: <next 2 tasks + why>

# Project invariants — staged
The authoritative invariants table (with Active-from gates) lives in
MASTER_IMPROVEMENT_PLAN.md. Enforce ACTIVE invariants as law; treat
pre-activation invariants as advisory in new work. Two are unconditionally
active now: never delete entries (status+tombstone instead) for manual edits,
and IDs/tombstones are append-only. Also always: never hand-edit data/*.json;
never put model calls in the deterministic build path.

# Working agreements (standing rules — added 2026-07-18)
1. **Committed-artifact rule.** Any artifact the user is meant to review is
   written to a file and committed BEFORE being shown to the user. Chat-only
   deliverables have been lost three times to session restarts (the WS0-T3
   validation sample, the outreach drafts, and nearly the cascade analysis).
   Reports, specs, samples, drafts, delta tables — all land on disk first.
   **1a. The missing half — PUSH, don't just commit (added 2026-07-30).**
   Board records and gate verdicts **push to origin at the end of every foreman
   run, whether or not their branch has merged.** Committed-but-local on an
   unmerged branch is the E18 failure with extra steps: the artifact exists,
   nobody else can see it, and a crash erases it exactly like a chat-only
   deliverable. Found in practice — this session's entire E21/E23 release-gate
   audit trail (two gate verdicts, a measurement record, and a correction to a
   published figure) sat local-only on an unmerged branch until a durability
   check caught it. **The check is one command:** `git ls-remote --heads origin
   <branch>` — empty means the record does not exist anywhere but this machine.
2. **Field-level delta rule.** Any transformative data operation (a rebuild,
   reduction, relabel, migration) publishes a full field-level before/after
   delta across every affected field plus entry-count/ID-set. Unintended
   deltas are DEFECTS, not noise; each intended delta is enumerated and
   justified. red-reviewer gates on this delta — a "pure" operation that moves
   fields it did not declare fails the gate. (Origin: the WS0-T3 field-cut
   silently relabelled 372 AIAAIC entries through description→classifier
   coupling — docs/audits/WS0-T3-cascade-2026-07-18.md.)
3. **Idle is not done (added 2026-07-29).** An agent's completion claim is
   verified by READING THE TREE — specifically, the presence of the
   deliverable's distinguishing content (grep for vocabulary the task would
   have introduced), not the absence of errors and not the agent's own
   summary. **Idle summaries describing PRIOR deliverables are a known
   failure shape** and read as completion if you don't check. Gates go idle
   without sending the verdict; specialists go idle with the work unstarted
   and the tree clean, which looks identical to "nothing broke." A verdict or
   a deliverable that was never sent does not exist. Four occurrences across
   three agents in a single session (2026-07-29: the conduct-half specialist
   died with everything uncommitted and the suite red; the gate went idle
   twice without its verdict and delivered only when asked directly; the
   specialist then went idle mid-task with the D22 register unstarted) — that
   is a rate, not a coincidence. **Corollary, the replace-vs-re-prompt
   heuristic: repeated idle-without-progress LATE IN A LONG CONTEXT is a
   REPLACE signal, not a re-prompt signal.** Late-context agents degrade
   exactly this way — going idle mid-task and summarizing past work instead
   of doing new work. When remaining scope is small and well-defined, kill
   the instance and dispatch a FRESH specialist with a self-sufficient brief:
   a clean context executing a clear brief beats a saturated one being
   reminded. Re-prompt at most once, then replace.
4. **Specs and audits are RECORDS first, sources never — supersede, don't
   rewrite (added 2026-07-30).** When a dated artifact (a spec, an audit, a
   ruling, an exit checklist) is overtaken by later work, **preserve the
   original text, add a dated update naming exactly which half changed, and
   mark it do-not-regenerate.** Never edit the original claim to make it
   current: the paragraph is the record of what was true when written *and* of
   the finding that produced the correction, and rewriting it destroys that
   record to fix a tense. **The do-not-regenerate marker is the load-bearing
   part** — a dated spec is exactly the kind of artifact a future pass mistakes
   for a source, which is how retired text gets reintroduced. Contrast with
   *live* surfaces (`README`, `NOTICE-DATA`, `.reuse/dep5`, `SOURCE_LICENSES`
   cells, a release notice): those state current state and **are corrected in
   place**, because a notice that hedges its own currency is not a notice. The
   test is what the artifact is *for*: describing a moment, or describing now.
   Origin: schema-architect used this on the WS0-T4 audit when its OECD half
   was overtaken; applied again 2026-07-30 to `docs/specs/WS0-T3-rescoped-2026-07-18.md`
   after E23 retired a sentence it quoted as current.
5. **The artifact is evidence; the verdict is testimony (added 2026-07-30).**
   A gate's PASS/BOUNCE **verdict text lands in the board commit**, not only
   in the session transcript. Record the verdict, its defects/advisories, and
   the evidence the reviewer says it measured — the foreman is the board's
   only writer, so this is the foreman's job at protocol step 6, not the
   reviewer's. **Why:** a deliverable's artifacts are re-derivable from the
   repo forever, but a verdict that exists only in a transcript cannot be
   checked by anyone later — including by the next session, which is exactly
   when it is relied on. A future reader must be able to tell "this was
   independently gated, here is what the gate measured" from "the board says
   it passed." **Consequence for phase-exit checklists:** evidence cells are
   marked **[R] re-derived** (measured now, command shown) or **[A] attested**
   (artifacts present, verdict is testimony), and **no criterion asserting a
   measurable property of the repo may be marked met on [A] alone.** Origin:
   a gate stated this limit about itself, unprompted, during the D8 re-verify
   — see PROGRESS.md's exit-checklist format entry. As agreement 4 takes hold,
   [A] rows should become rare; **if a checklist still needs [A] for a gate
   verdict, this agreement is not being followed.**
