# Peer Review: Minh (`luongnhatinh`) — Lab05 Integration

- **Người đánh giá (Reviewer):** Phạm Quốc Bảo ([simble2k](https://github.com/simble2k))
- **Tác giả PR (Author):** Lương Nhật Minh ([luongnhatinh](https://github.com/luongnhatinh))
- **Nhánh kiểm tra:** `feat/lab05-practice-ci-minh`
- **Các commit đối chiếu:** `cb4738f`, `6ee21ef`, `cc13cf8`, `9f4c7fb`

---

## 1. Tóm tắt phạm vi review

Nhánh `feat/lab05-practice-ci-minh` của Minh đảm nhiệm:
1. Hiện thực bài thực hành warm-up Python tương tác SQLite (`practice/school_repo.py` D1–D3).
2. Tích hợp các scripts di trú dữ liệu (`scripts/migrate.py`), script seed dữ liệu giả lập (`scripts/seed.py`) và các file migration SQL (`sql/migrations/`).
3. Nâng cấp GitHub Actions workflow (`.github/workflows/ci.yml`) để tự động hóa kiểm tra bài tập D1–D3 và kiểm soát điểm SQL đạt 15/15.
4. Báo cáo minh chứng cá nhân tại `docs/lab5/luongnhatinh/`.

---

## 2. Đánh giá kỹ thuật chi tiết

### A. Python School Repository (`practice/school_repo.py`)
- **Phòng chống SQL Injection (D1):**
  - Hàm `add_student` sử dụng câu lệnh tham số hóa chuẩn với placeholder `?`:
    `cur = con.execute("INSERT INTO students (name, year, program) VALUES (?, ?, ?)", (name, year, program))`
  - Đã kiểm tra chuỗi injection `Robert'); DROP TABLE students;--`: dữ liệu được lưu dưới dạng chuỗi thuần túy, bảng `students` không bị ảnh hưởng.
  - Gọi `con.commit()` đầy đủ và trả về `cur.lastrowid` chính xác.
- **Tính điểm trung bình (D2):**
  - `average_grade` xử lý đúng trường hợp không có điểm hoặc mã môn không hợp lệ bằng cách trả về `None`, làm tròn 2 chữ số thập phân (`round(float(row[0]), 2)`).
- **Bảng điểm sinh viên (D3):**
  - `transcript` thực hiện phép `JOIN` giữa `enrollments` và `courses` qua `course_code = code`, lọc theo `student_id` và sắp xếp tăng dần theo tiêu đề môn học (`ORDER BY c.title`).
- **Kết quả test:** Chạy `pytest -q practice/test_school_repo.py` đạt **5/5 passed**.

### B. Migrations và Idempotency
- Đã chạy kiểm tra `python scripts/migrate.py assistant-analysis.db` hai lần liên tiếp:
  - Lần 1: `apply 001_init.sql`, `apply 002_add_faq.sql`.
  - Lần 2: `skip 001_init.sql`, `skip 002_add_faq.sql`.
- Migration có cơ chế ghi nhận phiên bản đã áp dụng vào bảng quản lý di trú, đảm bảo tính idempotent tuyệt đối khi chạy lại nhiều lần.
- Script `scripts/seed.py` sinh đúng 300 tương tác giả lập có trọng số hợp lý và có cơ chế fallback sang `sqlite3` thuần khi chưa import được ORM.

### C. Nâng cấp CI (.github/workflows/ci.yml)
- Minh đã bổ sung bước thực thi `practice/test_school_repo.py` và tạo `school.db` để chạy `check.py`.
- `check.py` được bổ sung kiểm tra mã thoát (exit code 1 khi score < 15), giúp CI có thể ngăn chặn hiệu quả các PR chưa hoàn thành bài tập SQL.
- File `.gitignore` đã bổ sung các mẫu bỏ qua cơ sở dữ liệu (`*.db`, `*.sqlite`), tránh làm bẩn git tree.

---

## 3. Kết luận và Khuyến nghị

- **Trạng thái:** **APPROVED / LGTM** (Looks Good To Me).
- **Đóng góp tích cực:** Phần bài làm của Minh chuẩn chỉ, tuân thủ chặt chẽ contract đã thống nhất tại [PLAN_TUAN5.md](file:///c:/Users/Windows/Downloads/PLAN_TUAN5.md), không gây xung đột với tầng Database của Bảo hay API của Dương. Sẵn sàng để Tech Lead merge vào nhánh chính.
