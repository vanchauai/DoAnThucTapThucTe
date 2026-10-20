package com.doanthuctap.desktop.network;

/**
 * ApiException: Lớp exception custom để đóng gói các lỗi trả về từ API (ví dụ 401, 404, 500)
 * Giúp các Controller dễ dàng bắt lỗi và hiển thị thông báo.
 */
public class ApiException extends RuntimeException {
    private final int statusCode;

    public ApiException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }

    public ApiException(String message, Throwable cause) {
        super(message, cause);
        this.statusCode = 0; // Local error (e.g. network issue)
    }

    public int getStatusCode() {
        return statusCode;
    }
}
