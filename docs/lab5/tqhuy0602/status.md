# Lab05 — Trần Quốc Huy (`tqhuy0602`)

Nhánh `feat/lab05-config-huy` bắt đầu từ `main` tại `e468493`. `Settings` đọc `DATABASE_URL` và `SESSION_SALT` theo thứ tự ưu tiên biến môi trường, `.env`, rồi mặc định. Mặc định `sqlite:///assistant.db` và salt có sẵn dùng cho bài thực hành cục bộ. Đặt một salt riêng trong `.env` và giữ nguyên qua các lần chạy với cùng DB. Có thể tạo salt bằng `python -c 'import secrets; print(secrets.token_hex(32))'`. Cấu hình báo lỗi khi hai biến này được đặt thành chuỗi rỗng hoặc toàn khoảng trắng. Salt được loại khỏi `repr`, `model_dump()` và `model_dump_json()`.

| Hạng mục | Minh chứng |
| --- | --- |
| Q1–Q15 | [Lời giải](my_answers.sql), [checker 15/15](sql-check.txt) |
| D1–D3 | [School repository](school_repo.py), 5 test của học liệu qua, gồm SQL injection |
| R1–R2 | [Bản thực hành](feedback_repository.py), [3 test](test_feedback_repository.py) qua trên starter |
| H2 | [SQL](h2.sql), [kết quả chạy trên SQLite với 300 interaction giả lập](h2-result.md) |
| H3 | [Phần rà soát schema và quyền riêng tư](data-model-privacy.md) |
| Tích hợp | [Kết quả kiểm thử và log restart](tests.txt) |
| Review Dương | [Ghi chú tái hiện lỗi timezone của feedback](review-duong.md) |

Nhánh `main` ở commit gốc chưa có repository Lab05. Ba test riêng tư tự bỏ qua ở bản đó, và cả ba chạy trên bản kiểm tra ghép với API của Dương tại `3f51c7b` (đã tích hợp repository của Bảo). Demo Uvicorn dùng DB tạm và hai tiến trình. Cả hai interaction trỏ về cùng mã phiên đã hash, feedback cũ còn sau restart, và SQLite không chứa session ID thô, nội dung chat hoặc salt.

## Chạy lại bài thực hành

Học liệu Lab05 tại commit `d795a1a09f430d83b0c69b45da1689984a1254b5` cung cấp schema, checker, dữ liệu mẫu, test và starter. Đặt `LAB05` trỏ đến thư mục `lab05` của học liệu, rồi chạy từ root của repo nhóm với `pytest` và SQLModel 0.0.22 đã cài.

```sh
evidence_dir="$PWD/docs/lab5/tqhuy0602"
school_dir=$(mktemp -d)
cp "$LAB05"/practice/check.py "$LAB05"/practice/expected.json "$LAB05"/practice/make_school_db.py \
  "$LAB05"/practice/school.sql "$LAB05"/practice/test_school_repo.py "$school_dir/"
cp "$evidence_dir/my_answers.sql" "$evidence_dir/school_repo.py" "$school_dir/"
(cd "$school_dir" && python make_school_db.py && python check.py && python -m pytest -q test_school_repo.py)

personal_dir=$(mktemp -d)
cp "$evidence_dir/feedback_repository.py" "$evidence_dir/test_feedback_repository.py" "$personal_dir/"
(cd "$personal_dir" && PYTHONPATH="$LAB05/starter/src" python -m pytest -q test_feedback_repository.py)
```

Nguồn và phạm vi hỗ trợ AI được ghi trong [nhật ký AI](../../ai-use-log.md). Reviewer của phần cấu hình theo vòng nhóm là `pqquyenn`.
