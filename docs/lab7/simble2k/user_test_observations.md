# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Hà  Date: 2026-11-27
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Typed `"118 credits có đăng kí làm khóa luận được kh"` (mixing English, Vietnamese, and shorthand `"kh"`). | Expected the assistant to recognize `"118 credits"` and `"khóa luận"` and answer whether 118 credits meets the thesis rule. | KB documents only index full English keywords; the chat input placeholder (`"Ask about fees, offices or the handbook…"`) did not warn against Vietnamese/shorthand, and escalation repeated Training Office I.101 without English-rephrase guidance. | Update `st.chat_input` placeholder to state English-only / no shorthand, and show an actionable rephrase tip when mixed/shorthand queries escalate. |
| 2 | Typed `"tui mất studnet card thì làm lại ở đâu"` (Vietnamese + typo `"studnet"`) and received the `S26#3` answer (`Student Affairs, room I.102`). | After seeing the first mixed-language query fail and the second succeed despite a typo, they felt the AI handled shorthand and mixed English/Vietnamese inconsistently. | BM25 matched the standalone English token `"card"` in `S26#3`, whereas `"khóa luận"` + `"credits"` without `"thesis"` fell below `RETRIEVAL_MIN_SCORE=2.0`. | Explain clearly in the escalation tip that only full English keywords are indexed so users know why mixed phrasing may miss. |
| 3 | Sent multiple retries across the session (5 `/v1/chat` turns recorded in the demo DB before matching `H26#5.3`) and left `👍 Helpful` / `👎 Not helpful` unclicked (`0` feedback rows). | Expected a direct shortcut to re-ask with the right English phrasing instead of guessing keywords repeatedly. | Escalated answers offered no clickable English-question suggestion directly below the response. | Render one-click `"💡 Try in English: ..."` suggestion buttons below escalated mixed-language turns. |

The one change we made (commit link): https://github.com/baoduong2342007/assistant_core_lab/commit/c655f34a440df689cf1b26f3c2c642c4ad183fef (`c655f34` — English-rephrase guidance & one-click suggestions in `ui/logic.py`, `ui/app.py`, `tests/test_lab7_bao_h1.py`)
Before / after screenshot (1280x800 viewport, query `"118 credits có đăng kí làm khóa luận được kh"`):
- Before: [h1_before_mixed_query.png](screenshots/h1_before_mixed_query.png)
- After: [h1_after_mixed_query.png](screenshots/h1_after_mixed_query.png)
