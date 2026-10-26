# Week 3 — actual submission status (2026-10-25)

This index records classroom work and remaining evidence, not a self-awarded rubric score.

## Repository / commits / CI

- Repo: https://github.com/baoduong2342007/assistant_core_lab
- Integrated base: PR #1 (merged), main commit d632215.
- Dương foundation/integration: PR #16; see live PR for current head, review and merge state.
- CI: use check links on those PRs for exact commit evidence; the PR16 report records local checks
  and a clean-clone validation separately in docs/foundation-validation.md.
- Existing v0.3-core tag points to e975675 before the reviewed merge; it is not presented as completed
  release verification. No new release tag is created by this classroom integration.
- Bootcamp repo: https://github.com/baoduong2342007/python-boostcamp . Its W3/homework status was not
  verified in this task; no py-w3-done completion claim is made.

## Classroom evidence by member

| Member | Refactor / integration evidence | Worksheet | Status |
| --- | --- | --- | --- |
| Dương | [PR16](https://github.com/baoduong2342007/assistant_core_lab/pull/16); integrates core introduced by PR1 | [worksheet + measured metrics](../lab3/baoduong2342007/before_after.md) | Merged as a2ad759 after simble2k approval; CLI validation fixes, 19 added acceptance cases, measured worksheet, packaging and clean-clone evidence |
| Minh | [PR1 merged](https://github.com/baoduong2342007/assistant_core_lab/pull/1) | [worksheet](../lab3/luongnhatinh/before_after.md) | Tools/router/CI merged; decimal parser and worksheet measurements still need owner follow-up |
| Trần Quốc Huy | [PR19](https://github.com/baoduong2342007/assistant_core_lab/pull/19): config/logging fixes and owner evidence | [measured worksheet](../lab3/tqhuy0602/before_after.md) | 113 tests local + Python 3.10/3.12 CI passed at 579740b; peer review/merge pending |
| Quyền | Knowledge is present through PR1; no separate owner PR verified | [worksheet](../lab3/pqquyenn/before_after.md) | Owner verification pending |
| Bảo | Models/responders through PR1; [PR17 open](https://github.com/baoduong2342007/assistant_core_lab/pull/17) | [worksheet](../lab3/simble2k/before_after.md) | PR17 review and conflict resolution pending |

Baseline: ../lab3/baseline.md and baseline-evidence.json. Source manifest: reference/manifest.json.
Owner issues and acceptance criteria: ../tracking.md. Remaining gaps: ../lab3/open-items.md.
AI disclosure: ../ai-use-log.md. PR16 records Dương's actual changes; it does not claim original authorship
of the runtime modules introduced by Minh.

## Workflow and submission notes

The team integrated one shared refactor through PR1 before merging Dương's separate foundation PR.
This differs from the plan's foundation-first, owner-module PR order. Five-person module splitting also
differs from the tutorial's individual-refactor/comparison flow; disclose it and confirm instructor expectations.
The reviewer rotation is guidance; an available peer review is acceptable. GitHub's one-approval requirement
still applies; do not self-approve or bypass it. No claim is made that LMS submission has occurred.

## Homework status

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
