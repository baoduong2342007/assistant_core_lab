Làm trợ lý RAG giống như đi thi mở tài liệu: trước hết phải tìm đúng đoạn quy định liên quan thay vì tự đoán câu trả lời.
Nếu không có chunk nào hoặc điểm BM25 dưới ngưỡng 2.0, `RagAnswerer.answer` trả về `abstain` với `escalate=True` và `confidence=0.0` trước khi gọi model.
Sau khi model trả JSON, `parse_draft` trong code kiểm tra đúng schema, yêu cầu câu trả lời có ít nhất một nguồn và mọi `source_ids` đều nằm trong tập chunk đã truy xuất lượt đó.
Tuy nhiên trường hợp E19 cho thấy điểm tìm kiếm cao và ID hợp lệ vẫn có thể trật nội dung khi đoạn vắng thi `H26#7.2` không trả lời chuyện thi mở tài liệu.
Vì vậy tôi luôn phải đối chiếu nội dung chunk được trích và chạy lại bảng đánh giá trên cả các ca thất bại trước khi kết luận hệ thống đạt yêu cầu.
