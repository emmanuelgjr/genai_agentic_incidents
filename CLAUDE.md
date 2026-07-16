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
   for strays: untracked files the task did not deliberately create (usually
   shell-mangling artifacts — empty files with fragment-like names) are a
   defect the reviewer's git diff cannot see. PASS → done (paste the
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
