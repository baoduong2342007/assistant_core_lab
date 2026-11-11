# Review notes — Lab 5

Reviewed PR #45 at `9f4c7fbd358c0c84c349dece4a5c88cec3207c1f` and PR #46 at `1f49c5458cae166bcf9076837aa72d71bac5cdeb`. Changes-requested reviews were submitted on GitHub: [PR #45](https://github.com/baoduong2342007/assistant_core_lab/pull/45#pullrequestreview-5859811621) and [PR #46](https://github.com/baoduong2342007/assistant_core_lab/pull/46#pullrequestreview-5859810836).

## PR #46 — changes requested

- `Repository.record_interaction` checks for a session and then inserts it in separate statements. Two first requests for the same session can both see no row; one then fails with `UNIQUE constraint failed: chat_session.id`, causing a chat request to fail. Reproduced with two threads synchronized before insertion. The integration branch uses SQLite `ON CONFLICT DO NOTHING` and includes a concurrent regression test; this is not yet a fix on PR #46.
- SQLite foreign key enforcement is not enabled by `make_engine`; the declared relationships alone do not enforce referential integrity. R1 checks the interaction before adding feedback, but that is not equivalent to a database constraint. Agree whether to enable the pragma and test it for every connection. The ORM-created feedback table also lacks the rating CHECK present in migration 001.

## PR #45 — review findings

- `docs/lab5/luongnhatinh/h2-result.md` interprets seeded artificial latency and intent distributions as observed student demand and real application performance. `seed.py` chooses intents and latencies from preset random distributions, so the report should identify the output as synthetic and avoid causal claims about handbook lookup performance or user demand. Bảo’s H2 report makes similar claims.
- `scripts/migrate.py` uses `executescript()` within `with con`, but sqlite3 executescript commits a pending transaction before running its script. A failed migration can leave partial schema changes without a schema_version entry; rerun skip behavior is not proof of atomic rollback. Test failure handling or describe this limitation.

Independent checks on a clean export of #45: school repository tests 5 passed; SQL checker 15/15; migration applied 001 and 002 then skipped both on rerun; seed reported 300 synthetic interactions. These checks do not establish production performance or migration atomicity.
