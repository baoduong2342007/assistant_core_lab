# Remaining classroom / core items

These do not erase completed integration work or imply the entire team is finished.

| Item | Owner / tracking | Evidence / action |
| --- | --- | --- |
| Decimal credits/retakes silently parsed as integers | Minh, CORE-04 #6 | Fixed on branch fix/minh-classroom-closeout: reject non-integer expressions; 25 new tests and measured worksheet; awaiting peer review/merge |
| Unsupported provider accepted with a key | Huy, CORE-02 #4 | load_settings currently accepts arbitrary LLM_PROVIDER with a key; fixed in [PR19](https://github.com/baoduong2342007/assistant_core_lab/pull/19), stub/template only; awaiting merge |
| Broad except Exception in config/knowledge | Huy/Quyền, #4/#5 | Config narrowed in PR19; knowledge/CSV short-row follow-up remains Quyền's responsibility |
| Member acceptance / personal evidence | Each member; docs/tracking.md | Huy/Quyền invitations pending at last inspection; each person validates their own worksheet and PR ownership |
| Bảo's owner PR review / integration | PR #17 | Open and conflicts with main; H1/test wiring and worksheet evidence need follow-up |
| Bảo's owner PR review / integration | PR #17 | Main conflict resolved; real service/CLI H1 and fallback tests, corrected metrics added; peer review and personal confirmation remain |
| Release and fresh-clone at team level | CORE-08 #10, HOME-01 | Existing v0.3-core tag points to e975675 before review; do not force-move or claim it is verified release |
| Individual-refactor vs module-split process | Dương/team/instructor | Disclose five-person shared-module approach and confirm any required individual refactor evidence |

H1/H2/H3 are separate homework. Existing features/reports in PR #1 do not prove individual prompt,
three real improvements, personal PR or verified completion. Other members' reports are not edited here.
