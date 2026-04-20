# Báo cáo cá nhân

## Thông tin sinh viên

- Họ và tên: Hoàng Đức Hưng
- Mã sinh viên: 2A202600370
- Dự án: Day 13 Observability Lab

## Vai trò và phần việc đã thực hiện

Trong quá trình thực hiện dự án, tôi tập trung chủ yếu vào việc khảo sát hiện trạng hệ thống, xác định mức độ hoàn thiện của mã nguồn, hỗ trợ chuẩn bị môi trường chạy dự án và triển khai phần việc thuộc nhóm `Member D: load test + incident injection`.

Trước hết, tôi đọc và rà soát toàn bộ cấu trúc dự án để xác định hệ thống đã triển khai tới đâu. Tôi kiểm tra các thư mục `app/`, `scripts/`, `tests/`, `config/`, `docs/` và `data/`, từ đó tổng hợp được rằng dự án đã có sẵn phần backend FastAPI, cơ chế logging JSON, correlation ID, PII scrubbing, tracing, metrics nội bộ và bộ script phục vụ lab. Việc đọc toàn bộ mã nguồn giúp tôi hiểu rõ trạng thái hiện tại của dự án trước khi tiếp tục phát triển các phần còn lại.

Tiếp theo, tôi kiểm tra môi trường Python và quá trình cài đặt dependency. Trong lúc cài `requirements.txt`, tôi phát hiện lỗi do `pip` đang trỏ tới Python `3.14` toàn cục trong khi virtual environment của dự án đang dùng Python `3.12`. Tôi xác định thêm rằng `.venv` hiện tại chưa có `pip`, đây là nguyên nhân khiến quá trình cài đặt dễ bị lệch interpreter. Từ đó, tôi đưa ra hướng xử lý bằng cách dùng `uv` để tạo lại môi trường ảo với `--seed`, đảm bảo cài sẵn `pip` và giữ đúng phiên bản Python tương thích với các package như `pydantic-core`.

Phần đóng góp chính của tôi là triển khai và nâng cấp phần `Member D`. Tôi cải thiện script [scripts/load_test.py](C:/Users/hoang/Documents/Nhom08_402_Day13/scripts/load_test.py) để phục vụ tốt hơn cho việc kiểm thử tải và quan sát hệ thống. Phiên bản mới không chỉ gửi request tới endpoint `/chat`, mà còn hỗ trợ cấu hình `base-url`, số lần lặp, mức độ song song, timeout và file dữ liệu đầu vào. Sau mỗi đợt chạy, script tổng hợp thống kê như số request thành công/thất bại, throughput, độ trễ trung bình, P50, P95, P99 và đồng thời lấy thêm snapshot từ endpoint `/metrics` để hỗ trợ so sánh trước và sau khi bật incident.

Song song với đó, tôi nâng cấp script [scripts/inject_incident.py](C:/Users/hoang/Documents/Nhom08_402_Day13/scripts/inject_incident.py) để việc mô phỏng sự cố thuận tiện hơn trong lúc demo và phân tích. Script mới cho phép xem danh sách incident, xem trạng thái hiện tại, bật hoặc tắt từng sự cố như `rag_slow`, `tool_fail`, `cost_spike`, đồng thời in lại trạng thái sau khi thay đổi để người dùng theo dõi nhanh tình trạng hệ thống.

Ngoài việc chỉnh sửa code, tôi cũng kiểm tra sơ bộ trạng thái log của hệ thống. Dựa trên dữ liệu hiện có trong `data/logs.jsonl` và kết quả từ `scripts/validate_logs.py`, tôi xác định rằng dự án đã đạt mức cơ bản về JSON schema và PII scrubbing, nhưng chưa có đủ dữ liệu request thực tế để chứng minh đầy đủ correlation ID propagation và trace evidence. Nhận định này giúp nhóm biết chính xác phần nào đã xong ở mức code và phần nào còn cần chạy thực nghiệm để hoàn thiện báo cáo cuối cùng.

## Kết quả đạt được

- Hiểu rõ cấu trúc và tiến độ hoàn thiện hiện tại của toàn bộ dự án.
- Xác định đúng nguyên nhân lỗi môi trường Python/pip và đề xuất cách dựng lại môi trường bằng `uv`.
- Hoàn thiện phần script phục vụ `load test + incident injection` để nhóm có thể dùng cho demo, đo baseline và so sánh khi bật sự cố.
- Tạo nền tảng dữ liệu đầu vào cho các phần tiếp theo như dashboard, SLO và alert configuration.

## Khó khăn và cách xử lý

Khó khăn lớn nhất là môi trường chạy dự án chưa ổn định do lệch phiên bản Python giữa virtual environment và `pip` thực tế được gọi trong terminal. Tôi xử lý bằng cách kiểm tra trực tiếp interpreter, vị trí `pip` và cấu trúc thư mục `.venv`, sau đó xác định hướng khắc phục an toàn hơn là dùng `uv` để dựng lại môi trường đúng chuẩn.

Một khó khăn khác là dự án đã có sẵn nhiều phần mã nguồn nhưng chưa có đầy đủ bằng chứng chạy thực tế. Vì vậy, tôi ưu tiên nâng cấp các script hỗ trợ vận hành để nhóm có thể nhanh chóng sinh dữ liệu, bật/tắt sự cố và quan sát các chỉ số hệ thống, thay vì chỉ dừng lại ở mức đọc code.

## Hướng phát triển tiếp theo

Trong bước tiếp theo, tôi có thể tiếp tục hỗ trợ nhóm chạy thử toàn bộ hệ thống end-to-end sau khi môi trường được dựng ổn định, tạo baseline bằng load test, bật từng incident để thu thập log, metric và trace, sau đó chuyển các kết quả đó cho phần dashboard, SLO, alert và báo cáo nhóm.

## Tự đánh giá

Tôi đã hoàn thành tốt phần việc khảo sát hệ thống, hỗ trợ xác định lỗi môi trường và trực tiếp triển khai phần `Member D`. Phần đóng góp này giúp dự án tiến gần hơn tới giai đoạn có thể kiểm thử, trình diễn và thu thập evidence phục vụ chấm điểm.
