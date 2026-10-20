package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.config.AppConfig;
import com.doanthuctap.desktop.model.DataSource;
import com.doanthuctap.desktop.model.ListResponse;
import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import com.fasterxml.jackson.core.type.TypeReference;

import java.util.ArrayList;
import java.util.List;

/**
 * DataSourceService: Xử lý nghiệp vụ quản lý nguồn dữ liệu.
 */
public class DataSourceService {

    public ListResponse<DataSource> getDataSources() throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            ListResponse<DataSource> response = new ListResponse<>();
            List<DataSource> list = new ArrayList<>();
            
            DataSource d1 = new DataSource();
            d1.setId(1); d1.setName("Doanh_thu_thang_1.xlsx"); d1.setType("excel"); d1.setStatus("synced"); d1.setLastSyncedAt("2026-07-01T10:00:00");
            
            DataSource d2 = new DataSource();
            d2.setId(2); d2.setName("CRM_Database"); d2.setType("mysql"); d2.setStatus("pending"); d2.setLastSyncedAt(null);
            
            list.add(d1);
            list.add(d2);
            response.setData(list);
            response.setTotal(2);
            return response;
        }

        // Trick để parse ListResponse<DataSource> qua Jackson với generic type
        try {
            String json = ApiClient.getInstance().get("/data-sources", String.class);
            return ApiClient.getInstance().getObjectMapper().readValue(json, new TypeReference<ListResponse<DataSource>>() {});
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi parse dữ liệu API: " + e.getMessage(), e);
        }
    }

    public DataSource uploadExcel(java.io.File file, String name) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            DataSource d = new DataSource();
            d.setId(99);
            d.setName(name != null ? name : file.getName());
            d.setType("excel");
            d.setStatus("synced");
            d.setLastSyncedAt("2026-08-04T10:00:00");
            return d;
        }

        java.util.Map<String, String> fields = new java.util.HashMap<>();
        fields.put("name", (name != null && !name.trim().isEmpty()) ? name : file.getName());
        fields.put("column_mapping", "{}");

        return ApiClient.getInstance().postMultipart("/data-sources/upload", fields, "file", file, DataSource.class);
    }

    public com.doanthuctap.desktop.model.SyncResponse syncDataSource(int id) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            com.doanthuctap.desktop.model.SyncResponse mockRes = new com.doanthuctap.desktop.model.SyncResponse();
            mockRes.setMessage("Mock Sync");
            return mockRes;
        }
        return ApiClient.getInstance().post("/data-sources/" + id + "/sync", null, com.doanthuctap.desktop.model.SyncResponse.class);
    }
    public void deleteDataSource(int id) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            return;
        }
        ApiClient.getInstance().delete("/data-sources/" + id, Void.class);
    }

    public String getServiceAccountEmail() throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            return "mock-service-account@gserviceaccount.com";
        }
        try {
            java.util.Map<String, String> response = ApiClient.getInstance().get("/data-sources/gsheets/service-account-email", java.util.Map.class);
            return response.get("email");
        } catch (Exception e) {
            throw new ApiException("Không thể lấy email Service Account: " + e.getMessage(), e);
        }
    }

    public DataSource createGSheetsSource(String name, String url) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            DataSource d = new DataSource();
            d.setId(100);
            d.setName(name);
            d.setType("google_sheets");
            d.setStatus("pending");
            return d;
        }

        java.util.Map<String, Object> body = new java.util.HashMap<>();
        body.put("name", name);
        body.put("url", url);
        body.put("column_mapping", new java.util.HashMap<>());

        return ApiClient.getInstance().post("/data-sources/gsheets", body, DataSource.class);
    }
}
