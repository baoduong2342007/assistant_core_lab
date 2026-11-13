Tiêu đề: feat(lab05): hoàn thiện SQL và phân tích dữ liệu — Phan Quỳnh Quyền

Nội dung để dán vào phần mô tả PR:

---

## Problem and resulting behavior

Hoàn thành phần SQL và phân tích dữ liệu của Phan Quỳnh Quyền (`pqquyenn`) theo
Plan tuần 5: Q1–Q15, F1–F3, H2 có kết quả thực chạy và worksheet mô hình dữ liệu/H3.
Q12/Q14 giữ môn và sinh viên chưa có enrollment. F1/F2/H2 tính theo interaction;
F3 đếm sự kiện thumbs-down của topic khác NULL. Kết quả có thứ tự và tie-breaker rõ ràng.

## Scope, owner and dependencies

- Thêm `practice/my_answers.sql`, `sql/my_queries.sql` và 6 test kiểm tra shape,
  NULL, DB rỗng, thứ tự, cùng tên sinh viên và nhiều feedback/request.
- Thêm bằng chứng cá nhân D1–D3/R1–R2, runner tái lập, kết quả query và ER trong
  `docs/lab5/pqquyenn/`.
- Base: main `e468493`. Production DB/API/config và scaffold/migration/CI theo
  phân công Bảo/Dương/Huy/Minh; PR này không nhập các nhánh đó.
- Nhánh Minh `3f22c70` cũng có hai file SQL: nếu merge trước, xử lý add/add,
  giữ bản đã review và chạy lại kiểm tra; giữ phần scripts/practice Python của Minh.

## Validation actually run

Windows, Python 3.11.9, pytest 8.3.3, SQLModel 0.0.22, Ruff 0.6.9:

- Full suite: **328 passed**; Lab04 practice: **5 passed**.
- Checker học liệu: **15/15**; personal D1–D3: **5 passed**.
- Personal R1–R2: **4 passed**, gồm đóng engine và đọc lại feedback bằng engine mới.
- Ruff lint/format: pass. Warning BlockingPortal từ Starlette/AnyIO sẵn có.
- Migration học liệu: apply 001/002, lần hai skip. Seed DB sạch: **300 interactions,
  96 feedback, 59 sessions**. Shape F1/F2/F3/H2: **5×2 / 5×2 / 3×2 / 5×6**.
- Runner với starter và models Bảo tại `1f49c54` cho cùng kết quả tổng hợp.

Đây là kiểm tra cục bộ; chờ GitHub CI và API tích hợp sau khi nhóm merge phần nền.
Restart ở đây là test repository/engine, chưa phải demo restart HTTP server.

## Worksheet / evidence

- [Trạng thái và cách chạy lại](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/status.md)
- [Kết quả F1–F3](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/query-results.md)
- [H2 query + result](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/h2-result.md)
- [Worksheet mô hình dữ liệu/H3](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/data-model.md)
- [Kết quả kiểm thử](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/tests.txt)
- [Ghi chú review Huy](https://github.com/baoduong2342007/assistant_core_lab/blob/feat/lab05-sql-quyen/docs/lab5/pqquyenn/review-huy.md)

## AI use

Codex hỗ trợ đọc Plan/học liệu, viết SQL/snapshot/test/runner, kiểm tra và soạn
báo cáo cùng ghi chú review. Xem `docs/ai-use-log.md`. Quyền cần tự kiểm tra và
giải thích bài trước khi nộp; chưa khẳng định có peer approval hoặc nộp LMS.

## Reviewer

Reviewer dự kiến: **luongnhatinh (Minh)** theo vòng nhóm. Ghi chú review Huy trong
evidence chưa được đăng GitHub.
