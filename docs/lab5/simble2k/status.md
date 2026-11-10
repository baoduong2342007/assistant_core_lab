# Phạm Quốc Bảo (`simble2k`) — Lab05 Status Report

- **Ngày thực hiện:** 10/11/2026 (Asia/Ho_Chi_Minh)
- **Vai trò:** Database / Repository Engineer & Test Persistence Lead
- **Nhánh làm việc:** `feat/lab05-db-bao`
- **Base commit:** `e46849399c9c179f65e55b466ee7230fe69de344` (`origin/main`)
- **Tài liệu tham chiếu:** [PLAN_TUAN5.md](file:///c:/Users/Windows/Downloads/PLAN_TUAN5.md), [integration-contract.md](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/integration-contract.md)

---

## 1. Trách nhiệm được giao theo PLAN_TUAN5.md

Căn cứ Mục 4, Mục 5 và Mục 8 của kế hoạch:
- **Tầng Database/Repository (`src/assistant_api/db.py`):**
  - Định nghĩa 3 models SQLModel chuẩn hóa theo schema học liệu: `ChatSession`, `Interaction`, `Feedback`.
  - Triển khai hàm băm phiên bảo vệ quyền riêng tư `hash_session(raw, salt)` sử dụng SHA-256 (cắt lấy 16 ký tự hex).
  - Hoàn thiện phương thức `record_interaction` ghi phiên và tương tác trong cùng một transaction.
  - Hoàn thiện phương thức **R1** `add_feedback`: kiểm tra `request_id` có tồn tại trong `interaction` hay không, trả về `None` khi không tìm thấy (API ánh xạ thành 404), thêm bản ghi, commit và refresh để lấy ID tự tăng và timestamp từ DB.
  - Hoàn thiện phương thức **R2** `list_feedback`: sắp xếp mới nhất trước theo `created_at DESC, id DESC` và giới hạn số lượng `limit`.
  - Cung cấp phương thức `intent_stats` hỗ trợ endpoint thống kê admin.
- **Tầng Kiểm thử (`tests/test_lab5_db.py` & `tests/test_lab5_persistence.py`):**
  - Bộ kiểm thử đơn vị (Unit Test) chạy trên SQLite in-memory (`:memory:`) với `StaticPool` cho tốc độ tối ưu và cách ly hoàn toàn.
  - Bộ kiểm thử bền vững (Persistence Test) sử dụng file SQLite thực tế qua fixture `tmp_path` của pytest, kiểm tra dữ liệu tồn tại nguyên vẹn qua chu kỳ mô phỏng khởi động lại (restart) giữa 2 Engine/Repository độc lập.
- **Nhiệm vụ cá nhân & Đóng góp nhóm:**
  - Hoàn thành bài thực hành SQL Q1–Q15 đạt **15/15**.
  - Hoàn thành bài thực hành Python D1–D3 đạt **5/5 passed** (chống SQL injection).
  - Viết câu truy vấn kiểm toán H2, thực thi trên cơ sở dữ liệu giả lập 300 bản ghi và báo cáo kết quả.
  - Review nhánh PR `feat/lab05-practice-ci-minh` của Minh tại `docs/lab5/simble2k/review-minh.md`.
  - Phân tích và đóng góp chuyên sâu cho câu hỏi điểm thưởng H3 Bonus về PK/FK và ràng buộc schema.

---

## 2. Kết quả thực hiện chi tiết

### A. Tầng Database & Repository (`src/assistant_api/db.py`)
- Đã hoàn thiện toàn bộ mã nguồn trong [`src/assistant_api/db.py`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/src/assistant_api/db.py):
  - Khai báo các quan hệ ORM hai chiều (`Relationship`) sử dụng cấu hình tương thích `sa_relationship=relationship(...)`, hỗ trợ tương thích với hệ thống type annotations hiện đại.
  - Hàm `make_engine` tự động phát hiện URL bộ nhớ (`sqlite://`, `sqlite:///:memory:`) để gán `StaticPool` và cờ `check_same_thread=False`.
  - Hàm `init_db` gọi `SQLModel.metadata.create_all(engine)` đồng bộ schema.
  - Triển khai R1 (`add_feedback`) và R2 (`list_feedback`) theo đúng hợp đồng đề ra.

### B. Kiểm thử Unit Test (`tests/test_lab5_db.py`)
Bao gồm 6 test cases bao phủ toàn diện:
1. `test_session_id_is_hashed`: Xác minh session ID được băm với salt qua SHA-256 (16 ký tự hex), không lưu chuỗi session gốc.
2. `test_one_session_many_interactions`: Xác minh nhiều tương tác trong cùng 1 phiên chỉ sinh ra duy nhất 1 bản ghi `chat_session`.
3. `test_feedback_requires_existing_interaction`: Xác minh ID lạ trả về `None`, ID hợp lệ lưu thành công và trả về `Feedback` có ID tự tăng và timestamp.
4. `test_feedback_ordering_and_limit`: Xác minh danh sách feedback sắp xếp giảm dần theo thời gian và ID, tham số `limit` cắt đúng số lượng.
5. `test_intent_stats`: Xác minh tính đúng đắn của phép gom nhóm theo intent, tính trung bình độ trễ và đếm số lượt unresolved.
6. `test_record_interaction_fields`: Kiểm tra độ chính xác của các trường metadata (`topic`, `degraded`, `latency_ms`).

### C. Kiểm thử Bền vững qua Khởi động lại (`tests/test_lab5_persistence.py`)
Bao gồm 3 test cases xác minh tính bền vững trên đĩa:
1. `test_feedback_persists_across_restart`: Tạo file DB tạm bằng `tmp_path`, dùng Engine 1 ghi interaction và feedback, gọi `engine1.dispose()` mô phỏng tiến trình tắt. Khởi tạo Engine 2 mới tinh trỏ vào cùng file DB và xác minh dữ liệu feedback đọc lại nguyên vẹn từng trường (`id`, `request_id`, `rating`, `comment`, `created_at`).
2. `test_intent_stats_persists_across_restart`: Xác minh các chỉ số thống kê ý định giữ nguyên vẹn qua chu kỳ restart.
3. `test_chat_session_reuse_across_restart`: Tương tác ghi trước restart và tương tác ghi sau restart của cùng một người dùng vẫn liên kết chính xác vào cùng một bản ghi `chat_session` ban đầu.

---

## 3. Tổng hợp kết quả kiểm tra cục bộ (Local Verification)

| Lệnh kiểm tra | Kết quả ghi nhận | Trạng thái |
|---|---|:---:|
| `python -m pytest -q tests/test_lab5_db.py tests/test_lab5_persistence.py` | **9 passed** in 0.74s | **PASS** |
| `python -m pytest -q` | **331 passed** in 31.47s (toàn bộ 322 test cũ + 9 test mới) | **PASS** |
| `python -m ruff check .` | All checks passed! (0 lỗi) | **PASS** |
| `python -m ruff format --check .` | 45 files already formatted | **PASS** |
| `python practice/check.py` | **Score: 15/15 OK** (tại `docs/lab5/simble2k/sql-check.txt`) | **PASS** |
| `pytest -q practice/test_school_repo.py` | **5 passed** (gồm test SQL injection) | **PASS** |
| Migration & Seed 300 | `assistant-analysis.db` áp dụng 001/002, seed 300 interactions | **PASS** |
| Query kiểm toán H2 | Chạy thành công trên DB seed 300, xuất bảng tại `h2-result.md` | **PASS** |

---

## 4. Đóng góp cho H3 Bonus — Rà soát Schema và Ràng buộc Toàn vẹn

Căn cứ theo phân công nhóm tại Mục 4 [PLAN_TUAN5.md](file:///c:/Users/Windows/Downloads/PLAN_TUAN5.md) ("Bảo rà PK/FK/ràng buộc"), tôi đã tiến hành phân tích đối chiếu chuyên sâu:

### 4.1. Phân tích 6 khiếm khuyết nghiêm trọng của `sql/bad_schema.sql`

```sql
CREATE TABLE chats (
    id INTEGER,
    student_name TEXT,          -- real names stored with every message
    student_phone TEXT,
    message TEXT,               -- full raw message, kept forever
    answer TEXT,
    intent TEXT,                -- free text: 'fee', 'Fee', 'FEE', 'tuition'...
    time TEXT,                  -- '5/10/2026 9:03 PM' as text
    feedback TEXT,              -- '1,-1,1' comma-separated list of ratings
    latency TEXT                -- '120ms'
);
```

| # | Khiếm khuyết (Problem) | Tác hại kỹ thuật & Vận hành (Why it hurts) | Giải pháp chuẩn hóa (Fix) |
|---|---|---|---|
| **1** | **Thiếu Khóa chính (Missing Primary Key)** | Bảng không có `PRIMARY KEY` (chỉ có `id INTEGER` không ràng buộc `UNIQUE` hay `NOT NULL`). Dẫn đến rủi ro trùng lặp bản ghi, không thể thiết lập quan hệ 1-nhiều hay khóa ngoại từ bảng khác. | Định nghĩa `id INTEGER PRIMARY KEY` (hoặc `AUTOINCREMENT` trong SQLite) để đảm bảo tính định danh duy nhất. |
| **2** | **Vi phạm Quyền riêng tư (Privacy by Design Violation)** | Lưu trữ trực tiếp thông tin định danh cá nhân (PII: `student_name`, `student_phone`) và nội dung tin nhắn thô (`message`) vĩnh viễn. Nếu cơ sở dữ liệu bị lộ, toàn bộ thông tin nhạy cảm của sinh viên sẽ bị rò rỉ. | Loại bỏ hoàn toàn `student_name`, `student_phone`, `message`. Thay thế bằng `session_id` được băm SHA-256 có muối (`salt`), chỉ lưu trữ siêu dữ liệu (metadata: `intent`, `topic`, `latency_ms`). |
| **3** | **Vi phạm Chuẩn 1NF (Violation of First Normal Form)** | Cột `feedback TEXT` lưu danh sách đánh giá ngăn cách bằng dấu phẩy (`'1,-1,1'`). Không thể lập chỉ mục, không thể dùng hàm tổng hợp `AVG()` hay `COUNT()`, truy vấn lọc cực kỳ tốn chi phí CPU. | Tách thành một thực thể riêng biệt `feedback` có quan hệ 1-nhiều với `interaction` qua khóa ngoại `request_id`, mỗi hàng lưu đúng 1 lần đánh giá. |
| **4** | **Không có Ràng buộc Giá trị & Kiểu dữ liệu Chuẩn (No Value Constraints)** | Cột `intent` để dạng chuỗi tự do (`'fee'`, `'Fee'`, `'FEE'`) gây phân mảnh khi `GROUP BY`. Cột `latency` lưu chuỗi kèm đơn vị (`'120ms'`) khiến không thể thực hiện các phép tính số học (`AVG`, `SUM`). | Chuẩn hóa `latency_ms FLOAT DEFAULT 0.0`. Chuẩn hóa `intent VARCHAR(16)` viết thường nhất quán ở tầng logic ứng dụng. |
| **5** | **Thời gian lưu dạng Text không chuẩn hóa (Non-standard Timestamp Format)** | `time TEXT` lưu chuỗi `'5/10/2026 9:03 PM'`. Chuỗi này không theo chuẩn ISO 8601, không thể so sánh thứ tự thời gian bằng toán tử chuỗi hoặc dùng các hàm ngày tháng của SQL. | Sử dụng kiểu `TIMESTAMP` lưu theo định dạng chuẩn ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SS.fZ`). |
| **6** | **Thiếu Ràng buộc Toàn vẹn Tham chiếu (Missing Foreign Keys & Constraints)** | Toàn bộ dữ liệu nằm trong một bảng phẳng duy nhất (flat table). Không có ràng buộc kiểm tra miền giá trị (`CHECK constraint`) cho điểm đánh giá. | Thiết lập khóa ngoại `REFERENCES interaction(request_id)` và ràng buộc `CHECK (rating IN (-1, 0, 1))`. |

### 4.2. Đối chiếu Ràng buộc giữa SQL Migration (`001_init.sql`) và SQLModel (`src/assistant_api/db.py`)

1. **Ràng buộc CHECK giá trị Rating:**
   - Trong `001_init.sql`, bảng `feedback` có ràng buộc mức cơ sở dữ liệu: `CHECK (rating IN (-1, 0, 1))`.
   - Trong `SQLModel` (`src/assistant_api/db.py`), trường `rating: int` chỉ khai báo kiểu số nguyên. Việc kiểm soát miền giá trị được bảo vệ tại tầng ứng dụng (Pydantic schema `FeedbackIn` validate rating thuộc tập `{-1, 0, 1}` và trả về mã lỗi 422 nếu sai).
2. **Cơ chế Khóa ngoại (Foreign Keys) trong SQLite:**
   - Trong file migration SQL có khai báo `REFERENCES chat_session(id)` và `REFERENCES interaction(request_id)`.
   - **Lưu ý kỹ thuật quan trọng:** Trong SQLite, mặc định cơ chế kiểm tra khóa ngoại bị tắt (`PRAGMA foreign_keys = OFF`). Trừ khi ứng dụng chủ động gửi lệnh `PRAGMA foreign_keys = ON;` trên mỗi kết nối, SQLite sẽ không tự động từ chối bản ghi con mồ côi.
   - Do đó, việc phương thức `Repository.add_feedback` (R1) chủ động truy vấn kiểm tra sự tồn tại của `Interaction` trước khi lưu (`exists = db.exec(select(Interaction)...).first()`) đóng vai trò là chốt chặn phòng thủ vững chắc bảo vệ toàn vẹn dữ liệu ở cấp độ ứng dụng.
3. **Đánh Chỉ mục (Index Optimization):**
   - Hệ thống được thiết lập index trên: `request_id` (unique index), `session_id` (foreign key index), `intent` và `created_at`.
   - Điều này giúp các câu truy vấn thống kê (`GROUP BY intent`), lọc theo phiên (`WHERE session_id = ?`) và phân trang (`ORDER BY created_at DESC`) đạt độ phức tạp $O(\log N)$ thay vì phải quét toàn bộ bảng ($O(N)$ table scan).

---

## 5. Danh mục các tập tin thực hiện trên nhánh `feat/lab05-db-bao`

- [`src/assistant_api/db.py`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/src/assistant_api/db.py): Tầng dữ liệu SQLModel, các models, helper functions và Repository (R1, R2).
- [`tests/test_lab5_db.py`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/tests/test_lab5_db.py): 6 bài kiểm thử đơn vị cho Database/Repository.
- [`tests/test_lab5_persistence.py`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/tests/test_lab5_persistence.py): 3 bài kiểm thử bền vững qua restart với file SQLite tạm.
- [`pyproject.toml`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/pyproject.toml) & [`requirements.txt`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/requirements.txt): Bổ sung dependency `sqlmodel>=0.0.22`.
- [`.gitignore`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/.gitignore): Bổ sung bỏ qua các file cơ sở dữ liệu SQLite (`*.db`, `*.sqlite`, v.v.).
- [`docs/lab5/simble2k/status.md`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/status.md): Báo cáo tiến độ, kết quả và phân tích H3.
- [`docs/lab5/simble2k/sql-check.txt`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/sql-check.txt): Minh chứng kiểm tra SQL 15/15.
- [`docs/lab5/simble2k/tests.txt`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/tests.txt): Minh chứng chạy 331 tests passed.
- [`docs/lab5/simble2k/my_answers.sql`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/my_answers.sql): Bản snapshot câu trả lời SQL Q1–Q15.
- [`docs/lab5/simble2k/school_repo.py`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/school_repo.py): Bản snapshot bài thực hành Python D1–D3.
- [`docs/lab5/simble2k/h2.sql`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/h2.sql): Câu truy vấn kiểm toán H2.
- [`docs/lab5/simble2k/h2-result.md`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/h2-result.md): Báo cáo kết quả và phân tích truy vấn H2.
- [`docs/lab5/simble2k/review-minh.md`](file:///d:/APCS/HK4/Computational%20Thinking/assistant_core_lab/docs/lab5/simble2k/review-minh.md): Biên bản peer review PR của Minh.
