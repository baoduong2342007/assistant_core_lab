# Lab 5 — Dương: integration status (11 November 2026)

This branch locally merges Bảo’s PR #46 as an integration dependency. The PR remains open upstream and its concurrency bug was fixed on this integration branch; the fix still needs review by the owner. Huy’s dedicated configuration PR has not been published; the settings in this branch are provisional and must be reconciled with his work.

- API records interaction metadata, links chat request IDs to feedback, serves feedback and stats with admin authentication, and accepts injected repositories.
- A file-backed test and a real server stop/start confirmed feedback persistence.
- Personal practice snapshots were adapted from Minh’s PR #45 with Codex assistance; SQL checker reported 15/15 and the five practice tests passed. They are not claimed as independently written work. R1/R2 are based on Bảo’s PR #46, with an additional concurrency fix and test on this branch.
- H2 uses 300 synthetic records seeded by Minh’s scripts; results are generated examples, not real usage or measured API latency.
- `SESSION_SALT` must be set to a private, stable value for a real deployment. The built-in default is for local exercises only.
- The current resolved flag follows the starter convention of marking non-unknown intents resolved. A fee request rejected by core validation can still be labeled resolved; the core response does not expose success explicitly. Agree on a richer outcome contract before interpreting this statistic.

Review notes are in `review-prs.md`. No PR merge, remote review, tag, or LMS submission is claimed.
