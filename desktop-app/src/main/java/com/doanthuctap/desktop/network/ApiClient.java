package com.doanthuctap.desktop.network;

import com.doanthuctap.desktop.config.AppConfig;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.prefs.Preferences;

/**
 * ApiClient: Lớp tiện ích gọi API dùng chung bằng java.net.http.HttpClient.
 * Quản lý token xác thực (JWT), tự động đính kèm vào header Authorization.
 */
public class ApiClient {

    private static ApiClient instance;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final Preferences prefs;
    
    private static final String PREF_TOKEN_KEY = "jwt_token";

    private ApiClient() {
        this.httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(AppConfig.HTTP_TIMEOUT_SECONDS))
                .build();
        this.objectMapper = new ObjectMapper();
        this.prefs = Preferences.userNodeForPackage(ApiClient.class);
    }

    public static synchronized ApiClient getInstance() {
        if (instance == null) {
            instance = new ApiClient();
        }
        return instance;
    }

    public void setToken(String token) {
        prefs.put(PREF_TOKEN_KEY, token);
    }

    public String getToken() {
        return prefs.get(PREF_TOKEN_KEY, null);
    }

    public void clearToken() {
        prefs.remove(PREF_TOKEN_KEY);
    }

    public ObjectMapper getObjectMapper() {
        return objectMapper;
    }

    // --- Helper methods for HTTP verbs ---

    public <T> T get(String endpoint, Class<T> responseType) throws ApiException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(AppConfig.BASE_URL + endpoint))
                .GET();
        
        return execute(requestBuilder, responseType);
    }

    public <T> T post(String endpoint, Object body, Class<T> responseType) throws ApiException {
        try {
            String jsonBody = objectMapper.writeValueAsString(body);
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(AppConfig.BASE_URL + endpoint))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody));
            
            return execute(requestBuilder, responseType);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi serialize body JSON: " + e.getMessage(), e);
        }
    }

    public <T> T put(String endpoint, Object body, Class<T> responseType) throws ApiException {
        try {
            String jsonBody = objectMapper.writeValueAsString(body);
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(AppConfig.BASE_URL + endpoint))
                    .header("Content-Type", "application/json")
                    .PUT(HttpRequest.BodyPublishers.ofString(jsonBody));
            
            return execute(requestBuilder, responseType);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi serialize body JSON: " + e.getMessage(), e);
        }
    }

    public <T> T patch(String endpoint, Object body, Class<T> responseType) throws ApiException {
        try {
            String jsonBody = objectMapper.writeValueAsString(body);
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(AppConfig.BASE_URL + endpoint))
                    .header("Content-Type", "application/json")
                    .method("PATCH", HttpRequest.BodyPublishers.ofString(jsonBody));
            
            return execute(requestBuilder, responseType);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi serialize body JSON: " + e.getMessage(), e);
        }
    }

    public <T> T delete(String endpoint, Class<T> responseType) throws ApiException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(AppConfig.BASE_URL + endpoint))
                .DELETE();
        
        return execute(requestBuilder, responseType);
    }

    public <T> T postForm(String endpoint, String formData, Class<T> responseType) throws ApiException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(AppConfig.BASE_URL + endpoint))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(formData));
        
        return execute(requestBuilder, responseType);
    }

    public <T> T postMultipart(String endpoint, java.util.Map<String, String> fields, String fileFieldName, java.io.File file, Class<T> responseType) throws ApiException {
        String boundary = "---Boundary" + System.currentTimeMillis();
        try {
            byte[] fileBytes = java.nio.file.Files.readAllBytes(file.toPath());
            String fileName = file.getName();
            
            java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
            
            // Text fields
            if (fields != null) {
                for (java.util.Map.Entry<String, String> entry : fields.entrySet()) {
                    baos.write(("--" + boundary + "\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
                    baos.write(("Content-Disposition: form-data; name=\"" + entry.getKey() + "\"\r\n\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
                    baos.write((entry.getValue() + "\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
                }
            }
            
            // File part
            baos.write(("--" + boundary + "\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
            baos.write(("Content-Disposition: form-data; name=\"" + fileFieldName + "\"; filename=\"" + fileName + "\"\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
            baos.write(("Content-Type: application/octet-stream\r\n\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
            baos.write(fileBytes);
            baos.write(("\r\n--" + boundary + "--\r\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
            
            byte[] multipartBody = baos.toByteArray();
            
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(AppConfig.BASE_URL + endpoint))
                    .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                    .POST(HttpRequest.BodyPublishers.ofByteArray(multipartBody));
            
            return execute(requestBuilder, responseType);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi upload file: " + e.getMessage(), e);
        }
    }

    // execute request chung
    private <T> T execute(HttpRequest.Builder requestBuilder, Class<T> responseType) throws ApiException {
        String token = getToken();
        if (token != null && !token.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + token);
        }

        HttpRequest request = requestBuilder.build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                if (responseType == Void.class || responseType == String.class) {
                    return (T) response.body();
                }
                return objectMapper.readValue(response.body(), responseType);
            } else {
                throw new ApiException("Lỗi từ server: " + response.body(), response.statusCode());
            }
        } catch (IOException | InterruptedException e) {
            throw new ApiException("Lỗi kết nối mạng: " + e.getMessage(), e);
        }
    }
}
