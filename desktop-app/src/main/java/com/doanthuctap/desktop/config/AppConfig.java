package com.doanthuctap.desktop.config;

/**
 * AppConfig: Chứa các cấu hình chung của toàn bộ ứng dụng như Base URL của API, 
 * cấu hình timeout, cũng như cờ chuyển đổi giữa Mock API và API thực.
 */
public class AppConfig {
    // URL của Backend FastAPI
    public static final String BASE_URL = "http://localhost:8000/api/v1";
    
    // Cờ bật/tắt Mock Mode (nếu true, sẽ không gọi API thật mà trả về dữ liệu giả lập)
    public static final boolean IS_MOCK_MODE = false;

    // Timeout cấu hình cho HttpClient
    public static final int HTTP_TIMEOUT_SECONDS = 30;

    // Các vai trò người dùng (Roles)
    public static final String ROLE_ADMIN = "admin";
    public static final String ROLE_MANAGER = "manager";
    public static final String ROLE_EMPLOYEE = "employee";
}
