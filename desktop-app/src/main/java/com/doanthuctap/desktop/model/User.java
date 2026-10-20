package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * User: Đại diện cho thông tin người dùng được trả về từ API `/users/me`.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class User {
    private int id;
    
    @JsonProperty("full_name")
    private String fullName;
    
    private String email;
    private String role;
    
    @JsonProperty("created_at")
    private String createdAt;
    
    @JsonProperty("is_active")
    private boolean isActive;

    // Getters and Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public boolean isActive() { return isActive; }
    public void setActive(boolean active) { isActive = active; }
}

