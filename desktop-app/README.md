# Công Cụ Hỗ Trợ Tự Động Hóa Quy Trình Báo Cáo & Đồng Bộ Dữ Liệu Nội Bộ (Desktop App)

Đây là Client Giao diện Desktop được xây dựng bằng JavaFX, thuộc đồ án thực tập.
Ứng dụng giao tiếp với backend FastAPI để hiển thị Dashboard, Quản lý nguồn dữ liệu, và Tạo báo cáo.

## Yêu cầu hệ thống
- JDK 17 trở lên
- Apache Maven (đã cài đặt và thêm vào biến môi trường PATH)
- (Tùy chọn) IntelliJ IDEA hoặc Eclipse để mở code dễ dàng hơn.

## Cấu trúc thư mục chính
- `src/main/java/com/doanthuctap/desktop/`: Chứa mã nguồn Java (Model, Service, Controller).
- `src/main/resources/`: Chứa giao diện (FXML), style (CSS), và hình ảnh/icons.

## Cấu hình Backend
Backend API mặc định được cấu hình trỏ tới `http://localhost:8000/api/v1`. 
Bạn có thể thay đổi đường dẫn này trong file:
`src/main/java/com/doanthuctap/desktop/config/AppConfig.java` (biến `BASE_URL`).

**Lưu ý:** Nếu bạn chưa có backend chạy thực tế, ứng dụng đang được bật chế độ Mock API (`IS_MOCK_MODE = true` trong `AppConfig.java`). Bạn có thể chạy app ngay để xem giao diện.

## Hướng dẫn chạy ứng dụng

1. Mở Terminal (Command Prompt hoặc PowerShell).
2. Di chuyển vào thư mục dự án `desktop-app`:
   ```bash
   cd d:\DoAn\DoAnThucTapThucTe\desktop-app
   ```
3. Chạy lệnh sau để build và khởi chạy:
   ```bash
   mvn clean javafx:run
   ```

## Đóng gói ứng dụng (Build ra file chạy)
*Lưu ý: Để build ra file `.jar` chạy độc lập với JavaFX có thể cần thêm plugin shade, nhưng tạm thời bạn có thể dùng lệnh mvn để chạy.*
