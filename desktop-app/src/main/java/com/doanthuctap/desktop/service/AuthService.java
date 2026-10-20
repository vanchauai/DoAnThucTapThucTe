package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.config.AppConfig;
import com.doanthuctap.desktop.model.User;
import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.HashMap;
import java.util.Map;

import com.doanthuctap.desktop.session.UserSession;

/**
 * AuthService: Gọi API xác thực và quản lý thông tin người dùng hiện tại.
 */
public class AuthService {
    
    public User getCurrentUser() {
        return UserSession.getInstance().getUser();
    }

    public void login(String email, String password) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            // Dữ liệu giả lập
            if ("admin@company.com".equals(email) || "a@company.com".equals(email)) {
                ApiClient.getInstance().setToken("mock_jwt_token_123");
                User mockUser = new User();
                mockUser.setId(1);
                mockUser.setEmail(email);
                mockUser.setFullName("Nguyễn Văn A");
                mockUser.setRole(AppConfig.ROLE_MANAGER);
                
                UserSession.getInstance().setUser(mockUser);
                return;
            }
            throw new ApiException("Sai tài khoản hoặc mật khẩu (Mock)", 401);
        }

        String formData = "username=" + java.net.URLEncoder.encode(email, java.nio.charset.StandardCharsets.UTF_8)
                + "&password=" + java.net.URLEncoder.encode(password, java.nio.charset.StandardCharsets.UTF_8);

        // Gọi API login
        TokenResponse tokenResp = ApiClient.getInstance().postForm("/auth/login", formData, TokenResponse.class);
        ApiClient.getInstance().setToken(tokenResp.accessToken);

        // Gọi API lấy thông tin user
        fetchCurrentUser();
    }

    public void fetchCurrentUser() throws ApiException {
        if (AppConfig.IS_MOCK_MODE) return;
        User fetchedUser = ApiClient.getInstance().get("/users/me", User.class);
        UserSession.getInstance().setUser(fetchedUser);
    }

    public void logout() {
        ApiClient.getInstance().clearToken();
        UserSession.getInstance().clear();
    }

    // Helper class để parse token response
    @com.fasterxml.jackson.annotation.JsonIgnoreProperties(ignoreUnknown = true)
    private static class TokenResponse {
        @JsonProperty("access_token")
        public String accessToken;
    }
}

