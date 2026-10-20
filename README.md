# Hướng dẫn chạy và Kiểm thử End-to-End (E2E)

Dự án gồm 2 thành phần chính đã được tích hợp hoàn chỉnh:
- **Backend**: FastAPI (Python), MySQL
- **Desktop App**: JavaFX (Java)

Dưới đây là các bước để bạn chạy thông suốt cả hệ thống.

---

## 1. Khởi động Backend (FastAPI)

1. Mở Terminal / PowerShell và di chuyển vào thư mục backend:
   ```bash
   cd d:\DoAn\DoAnThucTapThucTe\backend
   ```
2. Cài đặt môi trường ảo (nếu chưa có):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Chạy lệnh migrate database (nếu dùng Alembic) để tạo các bảng mới nhất (như bảng `reports` vừa được thêm):
   ```bash
   alembic upgrade head
   ```
   *(Nếu bạn không dùng Alembic mà dùng Base.metadata.create_all, database sẽ tự tạo bảng khi chạy).*
4. Khởi động server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Mở trình duyệt: `http://localhost:8000/docs` để xác nhận Swagger UI đang hoạt động bình thường.

---

## 2. Khởi động Desktop App (JavaFX)

1. Mở một cửa sổ Terminal mới (không tắt cái cũ đang chạy Backend):
   ```bash
   cd d:\DoAn\DoAnThucTapThucTe\desktop-app
   ```
2. Chạy ứng dụng qua Maven:
   *(Lưu ý: Yêu cầu máy bạn phải cài Maven và Java 17)*
   ```bash
   mvn clean javafx:run
   ```
   Hoặc tốt nhất, hãy **mở IntelliJ IDEA**, import thư mục `desktop-app` và chạy trực tiếp từ `App.java` để tránh lỗi `mvn not found` như bạn đã gặp.

---

## 3. Các kịch bản kiểm thử (Test Cases)

**Kịch bản 1: Đăng nhập**
- Ở giao diện Login, nhập:
  - **Email:** `admin@company.com` (hoặc email có trong Database của bạn)
  - **Password:** Mật khẩu tương ứng.
- **Kỳ vọng:** Gọi API `POST /auth/login` thành công (form-urlencoded), lấy được JWT Token, và ứng dụng tự động chuyển sang trang Dashboard.

**Kịch bản 2: Xem danh sách nguồn dữ liệu**
- Bấm menu "Nguồn dữ liệu".
- **Kỳ vọng:** Desktop sẽ gọi `GET /data-sources`, lấy danh sách từ Database và hiển thị lên bảng TableView.

**Kịch bản 3: Đồng bộ dữ liệu**
- Tại màn hình "Nguồn dữ liệu", bấm chọn 1 dòng và bấm "Đồng bộ ngay".
- **Kỳ vọng:** Desktop gọi `POST /data-sources/{id}/sync`. Hệ thống hiển thị Alert thành công.

**Kịch bản 4: Tạo và xem báo cáo**
- Bấm menu "Báo cáo".
- Tại đây, hệ thống sẽ tự động gọi `GET /reports/history` để load danh sách các báo cáo cũ.
- Chọn tham số trên ComboBox và bấm **"Tạo báo cáo"**.
- **Kỳ vọng:** Desktop gọi `POST /reports/generate`. Backend sẽ tính toán số liệu (Metrics, Chart, Top Products), lưu vào Database (bảng `reports`), sau đó trả về cho Desktop. Màn hình Dashboard hoặc màn hình chi tiết sẽ cập nhật biểu đồ và thẻ số liệu tương ứng.

---

## 4. Xử lý lỗi phổ biến (Troubleshooting)

- **Lỗi 401 Unauthorized:** Token hết hạn. Ứng dụng Desktop có thể văng lỗi mạng ở Console, bạn chỉ cần bấm Đăng xuất và đăng nhập lại.
- **Lỗi CORS:** Đã được Backend xử lý trong `main.py` (`allow_origins=["*"]`). Nếu khi Deploy lên server thật, bạn cần cấu hình lại list domain trong file `.env`.
- **Date format mismatch:** Desktop đang parse chuỗi ISO8601 (`created_at`) về String qua Jackson. Nếu cần format đẹp hơn, có thể dùng `DateTimeFormatter` trong `UIUtils`.
