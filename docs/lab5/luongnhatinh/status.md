# Lương Nhật Minh (`luongnhatinh`) — Lab05 Status Report

Ngày thực hiện: **10/11/2026 (Asia/Ho_Chi_Minh)**.  
Cập nhật xử lý review: **11/11/2026 (Asia/Ho_Chi_Minh)**.  
Nhánh làm việc: `feat/lab05-practice-ci-minh`.  
Base commit (`origin/main`): `e46849399c9c179f65e55b466ee7230fe69de344`.

---

## 1. Trách nhiệm được phân công theo PLAN_TUAN5.md

Căn cứ Mục 4 và Mục 8 của kế hoạch:
- **Tích hợp Practice D1–D3:** Viết logic trong `practice/school_repo.py` bằng `sqlite3` thuần, sử dụng tham số hóa (`?` placeholders) chống SQL injection.
- **Nhập Scripts và Migrations:** Đưa `scripts/migrate.py`, `scripts/seed.py`, `sql/migrations/001_init.sql`, `sql/migrations/002_add_faq.sql`, `sql/my_queries.sql` vào repository.
- **Kiểm chứng Migration & Seed:** Chạy migrate 2 lần kiểm tra tính idempotent (lần 1 apply, lần 2 skip); seed 300 tương tác mẫu vào `assistant-analysis.db`.
- **Nâng cấp CI Workflow (`.github/workflows/ci.yml`):** Chạy kiểm thử tự động cho cả mã nguồn tuần cũ, warm-up Lab04 (`test_hello_api.py`), bài tập Lab05 (`test_school_repo.py`), đồng thời tự động tạo `school.db` và kiểm tra điểm SQL đạt 15/15.
- **Sản phẩm cá nhân:** Hoàn thành Q1–Q15 (15/15), câu query phân tích H2 kèm kết quả chạy thực tế, lưu minh chứng tại `docs/lab5/luongnhatinh/`.
- **H3 Schema Verification:** Kiểm tra tính toàn vẹn giữa migration SQL (`001_init.sql`) và model ORM (`assistant_api/db.py`).

---

## 2. Kết quả thực hiện chi tiết

### A. Practice Python (D1–D3)
- Đã hoàn thiện 3 hàm trong `practice/school_repo.py`:
  - `add_student`: Insert sinh viên có tham số hóa, commit transaction và trả về `cur.lastrowid`.
  - `average_grade`: Tính `AVG(grade)` theo mã môn, làm tròn 2 chữ số thập phân, trả `None` khi không có điểm hoặc môn học không tồn tại.
  - `transcript`: Sử dụng `JOIN` giữa `enrollments` và `courses`, lọc theo `student_id`, sắp xếp tăng dần theo tiêu đề môn học (`ORDER BY c.title`).
- Chạy `pytest -q practice/test_school_repo.py`: **5 passed** (bao gồm bài test chống SQL injection với chuỗi `Robert'); DROP TABLE students;--`).

### B. Practice SQL (Q1–Q15)
- Đã hoàn thành toàn bộ 15 câu truy vấn trong `practice/my_answers.sql`.
- Chạy `python practice/check.py`: **Score: 15/15** tuyệt đối.
- Cải tiến `check.py` để thoát với exit code `1` nếu `score < len(ref)` (15), giúp CI có thể chặn đứng các commit chưa đạt điểm tối đa.

### C. Scripts & Migrations (Đã nâng cấp Atomic Rollback)
- Nâng cấp `scripts/migrate.py`:
  - Thay thế cách gọi `with con: con.executescript()` (vốn tự động commit trước script trong Python `sqlite3`, dẫn đến nguy cơ không rollback được các câu lệnh DDL trước đó khi có lỗi giữa chừng).
  - Sử dụng hàm chuẩn thư viện `sqlite3.complete_statement` để phân tách từng câu lệnh SQL và quản lý giao dịch hiển thị `con.execute("BEGIN IMMEDIATE") ... con.execute("COMMIT")`. Khi gặp lỗi, script kích hoạt `con.execute("ROLLBACK")` để hoàn nguyên toàn bộ DDL đã thực thi của file đó và không cập nhật `schema_version`.
- Chạy `python scripts/migrate.py assistant-analysis.db` lần 1:
  ```text
  apply 001_init.sql
  apply 002_add_faq.sql
  ```
- Chạy lần 2:
  ```text
  skip  001_init.sql
  skip  002_add_faq.sql
  ```
  => Đảm bảo tính idempotent và an toàn giao dịch tuyệt đối khi chạy lại.
- Bổ sung bộ test tự động [tests/test_migrate.py](file:///tests/test_migrate.py) đạt **3/3 passed** (kiểm chứng split statements, migration áp dụng & bỏ qua, và kiểm chứng rollback nguyên tử khi file SQL bị lỗi cú pháp giữa chừng).
- Chạy `python scripts/seed.py assistant-analysis.db 300`:
  - Seed thành công 300 interactions, 59 chat sessions và 96 feedback records.
  - Script hỗ trợ cơ chế fallback an toàn sang `sqlite3` thuần khi môi trường chưa cấu hình SQLModel.

### D. Nâng cấp CI (.github/workflows/ci.yml)
- Bổ sung lệnh chạy `practice/test_school_repo.py`.
- Bổ sung bước tạo `school.db` từ `school.sql` và kiểm tra SQL tự động:
  ```yaml
  - name: Run Pytest suite
    run: |
      python -m pytest -q
      python -m pytest -q practice/test_hello_api.py
      python -m pytest -q practice/test_school_repo.py

  - name: Check SQL practice answers
    run: |
      python practice/make_school_db.py
      python practice/check.py
  ```

### E. Query phân tích H2
- Đã xây dựng query H2 đánh giá độ tin cậy và độ trễ theo từng intent, chạy trên DB phân tích 300 records và lưu báo cáo chi tiết tại `docs/lab5/luongnhatinh/h2-result.md`.

---

## 3. Tổng hợp kết quả kiểm tra cục bộ (Local Verification)

| Lệnh kiểm tra | Kết quả ghi nhận | Trạng thái |
|---|---|:---:|
| `python -m pytest -q` | 325 passed (bao gồm cả `test_migrate.py`), 1 warning | PASS |
| `python -m pytest -q tests/test_migrate.py` | 3 passed (atomic rollback & idempotency) | PASS |
| `python -m pytest -q practice/test_school_repo.py` | 5 passed (100% test Part D) | PASS |
| `python -m pytest -q practice/test_hello_api.py` | 5 passed (giữ vững hồi quy Lab04) | PASS |
| `python practice/make_school_db.py` | Tạo `students` (8), `courses` (5), `enrollments` (17) | PASS |
| `python practice/check.py` | **15/15 OK** (Exit code 0) | PASS |
| `python scripts/migrate.py assistant-analysis.db` (lần 1) | apply `001_init.sql`, apply `002_add_faq.sql` | PASS |
| `python scripts/migrate.py assistant-analysis.db` (lần 2) | skip `001_init.sql`, skip `002_add_faq.sql` | PASS |
| `python scripts/seed.py assistant-analysis.db 300` | seeded 300 interactions | PASS |
| `python -m ruff check .` | All checks passed! | PASS |
| `python -m ruff format --check .` | 99 files already formatted | PASS |

---

## 4. Đối chiếu Schema và Đóng góp cho H3 Bonus

- **Rà soát `001_init.sql` và `src/assistant_api/db.py`:**
  - SQL migration khai báo `CHECK (rating IN (-1, 0, 1))` trên bảng `feedback`, trong khi SQLModel chỉ lưu `rating: int` và dựa vào tầng API validation.
  - SQL migration có khai báo Foreign Keys (`REFERENCES chat_session(id)`, `REFERENCES interaction(request_id)`). Trong SQLite mặc định Foreign Key enforcement bị tắt trừ khi chạy lệnh `PRAGMA foreign_keys = ON;`.
  - Bảng `faq` ở migration `002_add_faq.sql` lưu `updated_by VARCHAR(32)` theo role (staff role) chứ không lưu danh tính cá nhân, tuân thủ nguyên tắc Privacy by Design.
  - Lỗi của `bad_schema.sql`: Lưu raw text thời gian (`5/10/2026 9:03 PM`), lưu chuỗi gộp feedback (`1,-1,1` vi phạm dạng chuẩn 1NF), lưu PII (`student_name`, `student_phone`), không có Primary Key.

---

## 5. Tiếp thu và Xử lý Đóng góp Peer Review trên GitHub

Tại PR [#45](https://github.com/baoduong2342007/assistant_core_lab/pull/45), nhóm đã tiến hành review chéo:
1. **Phạm Quốc Bảo (`simble2k`):** Đã kiểm tra độc lập và **APPROVED** bài làm.
2. **Trương Quang Bảo Dương (`baoduong2342007`):** Đã chỉ ra 2 điểm kỹ thuật cần điều chỉnh và yêu cầu cập nhật:
   - *Yêu cầu 1 (Báo cáo H2):* Tránh suy diễn nhân quả về thời gian tra handbook hay nhu cầu thực tế của sinh viên từ dữ liệu giả lập sinh bởi `seed.py`.
     $\rightarrow$ **Đã xử lý:** Đã viết lại mục 3 của `docs/lab5/luongnhatinh/h2-result.md`, xác định rõ đây là *synthetic simulation data*, tập trung phân tích đối chiếu giữa kết quả tổng hợp SQL với các tham số phân phối xác suất ngẫu nhiên (`PLAN`, `WEIGHTS`, `random.gauss`) của generator để chứng minh độ chính xác logic của câu truy vấn.
   - *Yêu cầu 2 (Migration Rollback & Atomicity):* `executescript()` trong `with con` không đảm bảo rollback nguyên tử cho DDL khi có lỗi giữa chừng.
     $\rightarrow$ **Đã xử lý:** Nâng cấp `scripts/migrate.py` bóc tách từng câu lệnh qua `sqlite3.complete_statement` và bọc trong transaction `BEGIN IMMEDIATE` / `ROLLBACK`. Đồng thời viết mới file test `tests/test_migrate.py` kiểm chứng trường hợp script lỗi giữa chừng thì toàn bộ bảng tạm đều được rollback hoàn nguyên sạch sẽ.

---

## 6. Danh mục file cập nhật trong nhánh

- `practice/school.sql`
- `practice/make_school_db.py`
- `practice/school_repo.py` (D1, D2, D3)
- `practice/test_school_repo.py`
- `practice/my_answers.sql` (Q1–Q15)
- `practice/check.py` (cải tiến exit code validation)
- `practice/expected.json`
- `scripts/migrate.py` (nâng cấp atomic rollback)
- `scripts/seed.py`
- `sql/migrations/001_init.sql`
- `sql/migrations/002_add_faq.sql`
- `sql/bad_schema.sql`
- `sql/my_queries.sql`
- `.github/workflows/ci.yml`
- `.gitignore`
- `tests/test_migrate.py` (kiểm chứng migration atomic rollback & idempotency)
- `docs/lab5/luongnhatinh/status.md`
- `docs/lab5/luongnhatinh/sql-check.txt`
- `docs/lab5/luongnhatinh/tests.txt`
- `docs/lab5/luongnhatinh/h2.sql`
- `docs/lab5/luongnhatinh/h2-result.md`
