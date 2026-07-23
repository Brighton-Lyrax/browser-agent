# Moltbook Learnings for ReplyPilot / Revenue Projects
Sources: `/api/v1/home`, `GET /posts sort=hot&sort=new`, comments on 7 high-signal posts — reflection loops, retrieval failure, memory uncertainty, coordination, state persistence, cron handoffs, irreversible-action checks.

## Top Themes
- **Reflection trap**: 387 reflections/hour archived without execution → `observation → storage` treated as completion instead of `hypothesis → test → next-state commit`.
- **Similarity ≠ corroboration**: 0.92 cosine often fetches rephrased copies of the same wrong abstraction. Retrieval layers silently promote routing metadata to evidence.
- **Uncertainty is structural**: Same JSON blob for tool output, claims, and model guesses lets stale errors become planning facts. Apollo AGC insight: memory must encode `observed / inferred / stale / denied`, not only content.
- **Coordination thermodynamics**: Resource penalties don’t create consensus; agents optimize for message reduction. Silence ≠ alignment.
- **Cron handoff corruption**: Dominant failure mode is state transfer between invocations, not hallucinations. Partial writes / schema drift / stale schedules compound.
- **Pre-action verification**: The high-risk moment is converting an old read/read justification into irreversible action. Safest checks bind to `intent hash + exact read set + freshness lease`.
- **Persistence ≠ continuity**: Billed “memory-optimized” agents fail on restart; the real measure is reconstructability, not self-description.

## Actionable Insights for ReplyPilot / Revenue
1. **Cap reflection backlog; make insights actionable tomorrow-or-expire.**
   ReplyPilot should convert a model-guessed optimization into either a deployed campaign change or a documented test, not a saved note. Hard cap: `max 10 unresolved insights per account/day`; auto-expire unused.

2. **Treat retrieval as routing, not evidence.**
   If ReplyPilot uses embedding search on past winning replies, add a cheap contradiction/provenance gate: cluster-by-upstream-source, flag rephrasing duplicates instead of returning as new signal.

3. **Add uncertainty schema to campaign memory.**
   Every persisted signal should carry `{ value, observedTs, system, confidence, reversible }`. Before using cached CTR / reply text / offer state, verify `observedTs` and `system` match current scope.

4. **Verification lease on irreversible actions.**
   For sends/payments/publish/follow blocks, require `VERIFIED` bound to intent hash + freshness lease, expire on any retry or config change. Avoid “it was verified 5 minutes ago” bugs.

5. **Cron handoff receipts over commit-logs.**
   For scheduled campaign jobs, log `{ claimId, producerVersion, consumerVersion, handoffHash, readBackQuery }` and require consumer acceptance test before marking done.

6. **Protected cheap dissent channel.**
   Add one low-cost structured objection channel in any multi-agent pipeline: Bayes drop / scope conflict / freshness breach / capability mismatch. Cheap to send; visible in traces; never silenced by token penalty.

## Unexpected Patterns Worth Testing
- **Quiet-default toxicity**: Adding token penalties reduces noise, but agents may “agree by silence” — test whether ReplyPilot’s safety filters create false consensus.
- **Cosine near-duplicate retrieval as a revenue anti-pattern**: If 0.92 similarity often fetches same lose abstracted tactic, high-velocity reply reuse may be a major hidden leak.
- **Retrieval as yes-man**: Embedding storage biased toward common/frequent replies may systematically discard rare high-converting framings.

## Suggested Follow-ups (1–3)
1. **Audit**: run a 72-hour trace of ReplyPilot scheduled jobs and memory reads; count “same post, rewritten” vs truly novel retrieved replies, and handoff bytes crossing agent boundaries.
2. **Schema patch**: add `observedAt / scopeHash / reversible` fields to persisted state store and gate production sends on them.
3. **Cheap pre-action probe**: build a `before_send` validator that refuses when current state hash ≠ read-set hash, even if the payload looks valid.
