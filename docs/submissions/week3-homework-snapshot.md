# Historical homework notes retained from the earlier Week 3 index

These notes were copied from the previous index during the 2026-10-26 classroom closeout.
They are historical, not re-verified current homework status. In particular, PR21 has since merged;
old draft/pending statements below must not be used as a live status report. No homework is marked
complete by this documentation change. The classroom index is [week3.md](week3.md).

## Earlier homework status


H1 individual extension reports/three improvements/merged owner PRs, H2 bootcamp and H3 reflections are
outside this classroom task and are not marked complete. Existing report files are retained as received
from PR1; their presence is not proof that their claimed personal actions happened.

## Huy follow-up — 2026-10-25

- Core PR19: config/logging, 113 tests; CI runs [40204220330](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40204220330) and [40204220363](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40204220363) succeeded at 579740b. Later doc commits need their own current checks; see live PR.
- [H1 draft PR21](https://github.com/baoduong2342007/assistant_core_lab/pull/21): distinct --session-id proposal, 129 tests; depends on core19/HOME-01. --log-level already existed and is not claimed as new.
- [W3 PR56](https://github.com/baoduong2342007/python-bootcamp/pull/56): 3 official + 40 additional tests; member CI Python 3.10/3.12 passed; Ruff 0.6.9 local has six legacy W1 findings; actual CI 0.17.2 subprocess findings are addressed in PR56 (official test bytes preserved); see live PR checks.
- [E2E draft PR57](https://github.com/baoduong2342007/python-bootcamp/pull/57): 16 cases currently fail because shared CLI dependency #54 has no __main__.py; not ready to merge.
- [H3](../lab3/tqhuy0602/reflection.md) is an AI-assisted draft awaiting Huy's own reading/confirmation. Personal hours, peer approvals and LMS submission are not inferred.
- Code owner Trần Quốc Huy; Codex hỗ trợ toàn bộ, including generated implementation/tests/docs, assisted review, validation and Git/PR preparation.

Live Huy status verified after the earlier snapshot: PR19 is merged at 1ee4e9a with baoduong2342007 peer approval.
PR21 was rebased by the team onto main and remains draft; the v0.3-core tag still points to e975675,
so no new HOME-01 release verification is claimed. Bootcamp PR56 CI is now green at 23ad463
(runs40206335449/40206335489); PR57 still awaits the missing shared CLI implementation.
