# Lab05 — Phan Quỳnh Quyền (`pqquyenn`)

Thực hiện theo `PLAN_TUAN5 (1).md`, trên nhánh `codex/feat/lab05-sql-quyen`,
từ main `e46849399c9c179f65e55b466ee7230fe69de344`. Ngày kiểm tra: 13/11/2026.

| Phần việc | Sản phẩm / kết quả |
| --- | --- |
| SQL Q1–Q15 tích hợp và cá nhân | [Lời giải](../../../practice/my_answers.sql), [checker 15/15](sql-check.txt) |
| F1–F3 | [SQL tích hợp](../../../sql/my_queries.sql), [báo cáo](query-results.md), [JSON thực chạy](query-results.json) |
| H2 | [SQL](h2.sql), [kết quả và diễn giải](h2-result.md) |
| H3 / ER / dữ liệu dư thừa | [Worksheet mô hình dữ liệu](data-model.md) |
| Bài cá nhân D1–D3 | [school_repo.py](school_repo.py), [5 test học liệu pass](practice-tests.txt) |
| Bài cá nhân R1–R2 | [Snapshot](feedback_repository.py), [4 test](test_feedback_repository.py), [kết quả](r1-r2-tests.txt) |
| Shape, NULL, thứ tự, nhiều feedback/request | [6 test SQL](../../../tests/test_lab5_sql.py), trong full suite 328 passed |
| Review Huy theo vòng nhóm | [Ghi chú hỗ trợ bởi AI](review-huy.md), người dùng tự kiểm tra và gửi review |
| Kiểm tra và PR | [Lệnh / môi trường / giới hạn](tests.txt), [nội dung PR](PR.md) |

Q12 dùng LEFT JOIN/COUNT(e.student_id) giữ môn có 0 người học. Q14 dùng
LEFT JOIN/COALESCE giữ sinh viên chưa đăng ký môn. Q13 dùng EXISTS, mỗi sinh viên
xuất hiện một lần dù có nhiều điểm dưới 5; hai sinh viên cùng tên không bị gộp.
Q15 dùng NOT EXISTS. Marker và thứ tự cột tương thích checker học liệu.

Main tại base chưa có scaffold/scripts/migrations hay DB/API Lab05. Nhánh này
thêm hai file SQL tích hợp, test SQL và bằng chứng cá nhân. Runner dùng học liệu
ngoài repo, tạo DB tạm và báo lỗi nếu score không đạt 15/15. Minh sở hữu scaffold,
Python practice, migrations và CI; Bảo sở hữu DB production; Dương nối API.

## Chạy lại

Trong virtualenv đã cài requirements project, chạy từ root repo:

```powershell
git clone https://github.com/CSC10014-at-fit-hcmus/public_materials.git "$env:TEMP/quyen-public-materials"
git -C "$env:TEMP/quyen-public-materials" checkout d795a1a09f430d83b0c69b45da1689984a1254b5
python -m pip install sqlmodel==0.0.22
python docs/lab5/pqquyenn/verify.py "$env:TEMP/quyen-public-materials/lab05"
python -m pytest -q
python -m pytest -q practice/test_hello_api.py
python -m ruff check .
python -m ruff format --check .
```

SQLModel chỉ cần cho bài cá nhân/seed ở runner; nhánh SQL không sửa dependency
runtime main. Runner ghi lại log và query-results.json; thời lượng test/đường dẫn
temp có thể đổi. Đã chạy với starter gốc và models Bảo tại `1f49c54`, cùng kết quả.
Cách kiểm tra lại models Bảo sau khi fetch origin:

```powershell
python -c "import pathlib, subprocess, tempfile; p = pathlib.Path(tempfile.gettempdir()) / 'quyen-bao-db.py'; p.write_bytes(subprocess.check_output(['git', 'show', '1f49c5458cae166bcf9076837aa72d71bac5cdeb:src/assistant_api/db.py']))"
python docs/lab5/pqquyenn/verify.py "$env:TEMP/quyen-public-materials/lab05" --db-source "$env:TEMP/quyen-bao-db.py"
```

## Bàn giao

Nhánh Minh `3f22c70` cũng có hai đường dẫn SQL này. Nếu merge trước, xử lý add/add
ở `practice/my_answers.sql` và `sql/my_queries.sql`, giữ một bản canonical được
review và chạy lại 15/15/test SQL. Không chép đè toàn bộ practice/scripts của Minh.
D1–D3/R1–R2 ở đây là snapshot cá nhân.

Minh (`luongnhatinh`) là reviewer dự kiến. Người dùng tự push nhánh và mở PR về
main; chưa có PR, approval của người thật hoặc CI từ GitHub. Demo HTTP restart,
tích hợp API/config/DB, tag v0.5-data và nộp LMS do nhóm chốt trên main sau merge.
Query dùng dữ liệu giả lập thực chạy, không lấy số minh họa PDF làm kết quả.

Xem [nhật ký AI](../../ai-use-log.md). Quyền cần đọc, giải thích lời giải và kiểm
tra báo cáo/review trước khi nộp bài.
