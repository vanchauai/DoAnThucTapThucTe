package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.model.User;
import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import com.fasterxml.jackson.core.type.TypeReference;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UserService {

    public List<User> getUsers() throws ApiException {
        try {
            String json = ApiClient.getInstance().get("/users", String.class);
            return ApiClient.getInstance().getObjectMapper().readValue(json, new TypeReference<List<User>>() {});
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi parse danh sách người dùng: " + e.getMessage(), e);
        }
    }

    public User createUser(User user, String password) throws ApiException {
        Map<String, Object> body = new HashMap<>();
        body.put("email", user.getEmail());
        body.put("password", password);
        body.put("full_name", user.getFullName());
        body.put("role", user.getRole());
                
        return ApiClient.getInstance().post("/users", body, User.class);
    }

    public User updateUser(int id, User user, String newPassword) throws ApiException {
        Map<String, Object> body = new HashMap<>();
        body.put("email", user.getEmail());
        body.put("full_name", user.getFullName());
        body.put("role", user.getRole());
                if (newPassword != null && !newPassword.trim().isEmpty()) {
            body.put("password", newPassword);
        }
        
        return ApiClient.getInstance().put("/users/" + id, body, User.class);
    }

    public User toggleUserStatus(int id, boolean isActive) throws ApiException {
        Map<String, Object> body = new HashMap<>();
        body.put("is_active", isActive);
        return ApiClient.getInstance().patch("/users/" + id + "/status", body, User.class);
    }

    public void changeMyPassword(String oldPassword, String newPassword) throws ApiException {
        Map<String, Object> body = new HashMap<>();
        body.put("old_password", oldPassword);
        body.put("new_password", newPassword);
        ApiClient.getInstance().put("/users/me/change-password", body, String.class);
    }
}

