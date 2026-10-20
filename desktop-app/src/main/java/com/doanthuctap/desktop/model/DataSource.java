package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

/**
 * DataSource: Đại diện cho cấu hình nguồn dữ liệu đã kết nối.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class DataSource {
    private int id;
    private String name;
    
    @JsonProperty("source_type")
    private String type;
    
    @JsonProperty("config")
    private Map<String, Object> config;
    
    @JsonProperty("column_mapping")
    private Map<String, String> columnMapping;
    
    @JsonProperty("created_at")
    private String createdAt;
    
    private String status;
    
    @JsonProperty("last_synced_at")
    private String lastSyncedAt;

    // Getters and Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public Map<String, Object> getConfig() { return config; }
    public void setConfig(Map<String, Object> config) { this.config = config; }

    public Map<String, String> getColumnMapping() { return columnMapping; }
    public void setColumnMapping(Map<String, String> columnMapping) { this.columnMapping = columnMapping; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getLastSyncedAt() { return lastSyncedAt; }
    public void setLastSyncedAt(String lastSyncedAt) { this.lastSyncedAt = lastSyncedAt; }
}

