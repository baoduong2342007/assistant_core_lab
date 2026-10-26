# Lab 3 classroom submission index — 2026-10-26

Owner: Dương (`baoduong2342007`), coordination issue [#10](https://github.com/baoduong2342007/assistant_core_lab/issues/10).
Scope: CL-00 → CL-04 only, following Week3/plan.md. No H1/H2/H3 or release completion is asserted.
This is the classroom handoff index, not confirmation that an LMS submission has occurred.

## Repository and current validation

- Repository: [assistant_core_lab](https://github.com/baoduong2342007/assistant_core_lab). Package/import: assistant-core / assistant_core.
- Verified integrated commit: [`22f95b8`](https://github.com/baoduong2342007/assistant_core_lab/commit/22f95b8de7e00976204305859f6cec95329cbde3).
- Full suite: **208 passed** in the PR24 validation (171 base + 37 knowledge regressions), with Ruff
  check/format/BLE passed. Runtime fixes were integrated by the verified commit above.
- Its main-branch Python3.10/3.12 checks are all successful:

- [Foundation (3.10)](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40278501405/job/121426345844): success.
- [test-and-lint (3.10)](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40278501431/job/121426345654): success.
- [test-and-lint (3.12)](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40278501431/job/121426345631): success.
- [Foundation (3.12)](https://github.com/baoduong2342007/assistant_core_lab/actions/runs/40278501405/job/121426345516): success.

Machine-readable snapshot (PR merge SHAs, checks, issue states, access and validation provenance):
[classroom-evidence-2026-10-26.json](classroom-evidence-2026-10-26.json).
New documentation commits use their own PR checks; the links above remain evidence for the named code commit.

## Five-member contribution / worksheet handoff

All PRs linked in this table are merged. Shared core originally arrived through PR1; later owner/fix PRs
are credited separately instead of claiming every member originally authored the entire package.

| Member / assigned work | Merged evidence | Worksheet and measurements | Remaining classroom tracking |
| --- | --- | --- | --- |
| Dương — foundation, packaging, service/CLI integration, architecture and coordination | [PR16](https://github.com/baoduong2342007/assistant_core_lab/pull/16), [PR18](https://github.com/baoduong2342007/assistant_core_lab/pull/18); correction assistance on PR17/23/24 disclosed | [10-row worksheet, smells and reflections](../lab3/baoduong2342007/before_after.md), [metrics](../lab3/baoduong2342007/metrics.json) | #2/#8/#11 closed; #10 awaits peer review of this index and remaining member confirmations |
| Minh — pure tuition tools, router, Ruff/CI | [PR1](https://github.com/baoduong2342007/assistant_core_lab/pull/1), [PR23 parser/tests/worksheet correction](https://github.com/baoduong2342007/assistant_core_lab/pull/23) | [worksheet](../lab3/luongnhatinh/before_after.md), [metrics](../lab3/luongnhatinh/metrics.json) | #6/#9/#14 closed; follow-up corrections by Dương/Codex are attributed explicitly |
| Trần Quốc Huy — config, environment and JSON logging | [PR19](https://github.com/baoduong2342007/assistant_core_lab/pull/19) | [measured worksheet](../lab3/tqhuy0602/before_after.md), [metrics](../lab3/tqhuy0602/metrics.json) | #4/#12 closed; Huy confirmed worksheet on 2026-10-26; all 12 AST measurement entries reverified against reviewed Core snapshot |
| Phan Quỳnh Quyền — offices/handbook, sample data and search | [PR24 schema/CSV fixes, tests and owner documentation](https://github.com/baoduong2342007/assistant_core_lab/pull/24) | [worksheet](../lab3/pqquyenn/before_after.md), [metrics](../lab3/pqquyenn/metrics.json) | #5/#13 closed; corrections made with Dương/Codex are disclosed; no invented personal reading/hours |
| Phạm Quốc Bảo — models/errors, responder protocol, shared fixtures and fallback | [PR17](https://github.com/baoduong2342007/assistant_core_lab/pull/17), original shared models in [PR1](https://github.com/baoduong2342007/assistant_core_lab/pull/1) | [corrected worksheet](../lab3/simble2k/before_after.md), [metrics](../lab3/simble2k/metrics.json) | #7 closed; [#3](https://github.com/baoduong2342007/assistant_core_lab/issues/3) technical evidence closeout and [#15](https://github.com/baoduong2342007/assistant_core_lab/issues/15) personal worksheet confirmation remain |

All five users have repository write access; no invitation is pending in the snapshot.
Reviewer rotation is guidance. Actual peer approval still applies; no review is fabricated by this index.

## Baseline, integration behavior and supporting files

- Original starter/worksheets: [source manifest](../../reference/manifest.json) and [source note](../../reference/README.md).
  Runtime CSV/JSON remain sample lab data, not current university policy.
- Actual baseline: [baseline.md](../lab3/baseline.md), [captured commands/output](../lab3/baseline-evidence.json).
  The original fake provider is offline; print-only --test exit0 is not an assertion-suite pass.
- Integrated acceptance includes greeting, tuition 18+2 = 9,450,000 VND, Library B.201/hours,
  thesis source H26-5.3, unknown with empty sources and controlled provider fallback retaining source/degraded.
- Regression coverage includes decimal/negative/boundary credits, malformed CSV/JSON and expected DataError,
  CLI startup/request/usage exits, streams, EOF/quit, load-once data and stable rule-search ties.
- [Architecture/interface + three decisions](../architecture.md), [contracts](../contracts.md),
  [worksheet index](../lab3/before_after.md), [AI disclosures](../ai-use-log.md), [issue tracking](../tracking.md).
- Earlier clean-clone validation names the commit it tested: [report](../clean-clone-evidence.md).
  It is not presented as a fresh-clone run of today's latest commit or independent peer release verification.

## End-of-class handoff and remaining actions

The five PR/worksheet pairs above can be used as the end-of-class link list. Each member should verify
their own contribution/reflection before submitting. Dương prepares the shared package/index; each person
provides their own PR and worksheet. No deadline or LMS upload is invented here.

The earlier snapshot listed classroom issues **#3, #12, #15 and #10**. Huy subsequently confirmed
his worksheet on 2026-10-26; #12 is now closed with reviewed PR19 and reverified measurement evidence.
Other issue states in the [machine-readable snapshot](classroom-evidence-2026-10-26.json) remain historical;
consult GitHub for their current state. The code fixes identified during review are merged; this does not
claim all possible bugs are excluded. Dương coordinates the final shared index and submission.

## Workflow disclosure and homework boundary

The group used a five-person shared-module integration, with core introduced by PR1 before the separate
foundation/owner corrections. This differs from the plan's foundation-first sequence and the tutorial's
individual-refactor/comparison process. Describe actual contribution and confirm instructor expectations;
do not claim five independent full refactors or recreate history.

Existing v0.3-core points to an earlier commit; no release/tag is changed or certified here. HOME-01,
H1/H2/H3, bootcamp and py-w3-done are outside this classroom closeout. Earlier homework notes are retained
as an explicitly [historical snapshot](week3-homework-snapshot.md), not current completion evidence.
