# Week 3 Submission Summary — Team 03

## 1. Repository and Release Metadata

- **Repository**: [assistant_core_lab](https://github.com/baoduong2342007/assistant_core_lab)
- **Tag**: `v0.3-core`
- **Bootcamp Repository**: `python-boostcamp` (Tag: `py-w3-done`)
- **Package Distribution Name**: `assistant-core`
- **Import Name**: `assistant_core`

---

## 2. Team Member Deliverables & Contribution Matrix

| Member | Username | Module Responsibilities | Refactor PR | Worksheet | H1 Feature & Report | H3 Reflection |
|---|---|---|---|---|---|---|
| **Bảo Dương** | `baoduong2342007` | Skeleton, Packaging, Service, CLI, Architecture | `refactor/assistant-core-baoduong2342007` | [Worksheet](../lab3/baoduong2342007/before_after.md) | `--json` export ([Report](../lab3/baoduong2342007/ai_extension_review.md)) | [Reflection](../lab3/baoduong2342007/reflection.md) |
| **Trần Quang Huy** | `tqhuy0602` | Config, `.env.example`, JSON Logging | `refactor/assistant-core-tqhuy0602` | [Worksheet](../lab3/tqhuy0602/before_after.md) | `--log-level` override ([Report](../lab3/tqhuy0602/ai_extension_review.md)) | [Reflection](../lab3/tqhuy0602/reflection.md) |
| **Phan Quốc Quyền** | `pqquyenn` | Knowledge (OfficeDirectory, Handbook) | `refactor/assistant-core-pqquyenn` | [Worksheet](../lab3/pqquyenn/before_after.md) | List regulations ([Report](../lab3/pqquyenn/ai_extension_review.md)) | [Reflection](../lab3/pqquyenn/reflection.md) |
| **Lương Nhật Minh** | `luongnhatinh` | Tools (Tuition, parse credits), Router, Ruff, CI | `refactor/assistant-core-luongnhatinh` | [Worksheet](../lab3/luongnhatinh/before_after.md) | `--credit-rate` override ([Report](../lab3/luongnhatinh/ai_extension_review.md)) | [Reflection](../lab3/luongnhatinh/reflection.md) |
| **Nguyễn Tấn Bảo** | `simble2k` | Models, Errors, Responders, Fallback tests | `refactor/assistant-core-simble2k` | [Worksheet](../lab3/simble2k/before_after.md) | Exact Rule ID lookup ([Report](../lab3/simble2k/ai_extension_review.md)) | [Reflection](../lab3/simble2k/reflection.md) |

---

## 3. Rubric Verification Evidence

| Criterion (Lab 3 Tutorial Page 19) | Max Points | Verification & Location |
|---|---|---|
| Clean package structure; one responsibility per module | 2 | Standard `src/assistant_core` layout with 10 single-responsibility modules |
| Config from environment; `.env.example`; no secret in code or logs | 2 | `config.py` loads from env/`.env`; `.env.example` committed; `repr=False` masks secrets; structured JSON logs to stderr |
| Typed models; named exceptions; fallback path tested | 2 | Pydantic `Message`/`Response`/`Rule`; `AssistantError` hierarchy; `test_service_fallback_when_provider_fails` passes |
| Tests pass (≥ 10), including characterisation tests | 1 | **71 passing tests** covering characterisation, unit, integration, and CLI |
| Ruff check clean; dependencies pinned | 1 | Clean pass on `ruff check .`, `ruff format --check .`, `ruff check --select BLE .`; pinned in `requirements.txt` |
| Architecture note with interface and 3 decisions | 1 | Documented in `docs/architecture.md` with interface and 3 architectural decisions with rationales |
| H1: three documented improvements to AI-generated code | 1 | Detailed in `docs/lab3/<username>/ai_extension_review.md` for all 5 team members |
| **Total** | **10 / 10** | **All criteria fully met** |
