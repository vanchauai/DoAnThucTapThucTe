package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.config.AppConfig;
import com.doanthuctap.desktop.model.ListResponse;
import com.doanthuctap.desktop.model.ReportData;
import com.doanthuctap.desktop.model.ReportHistory;
import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import com.fasterxml.jackson.core.type.TypeReference;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * ReportService: Xử lý nghiệp vụ tạo báo cáo và xem lịch sử.
 */
public class ReportService {

    public ReportData generateReport(String periodType, String periodValue, boolean save) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            return mockReportData();
        }

        Map<String, Object> body = new HashMap<>();
        body.put("period_type", periodType);
        body.put("period_value", periodValue);
        body.put("save", save);

        return ApiClient.getInstance().post("/reports/generate", body, ReportData.class);
    }

    public ListResponse<ReportHistory> getHistory() throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            ListResponse<ReportHistory> response = new ListResponse<>();
            List<ReportHistory> list = new ArrayList<>();
            ReportHistory h1 = new ReportHistory();
            h1.setId(5);
            h1.setReportName("Báo cáo doanh thu Q2/2026");
            h1.setPeriodType("quarter");
            h1.setPeriodValue("Q2-2026");
            
            h1.setCreatedAt("2026-07-01T09:00:00");
            list.add(h1);
            
            response.setData(list);
            response.setTotal(1);
            return response;
        }

        try {
            String json = ApiClient.getInstance().get("/reports/history", String.class);
            return ApiClient.getInstance().getObjectMapper().readValue(json, new TypeReference<ListResponse<ReportHistory>>() {});
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi parse dữ liệu API lịch sử báo cáo: " + e.getMessage(), e);
        }
    }

    public ReportData getReportById(int id) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            return mockReportData();
        }

        try {
            String json = ApiClient.getInstance().get("/reports/" + id, String.class);
            return ApiClient.getInstance().getObjectMapper().readValue(json, ReportData.class);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi parse dữ liệu API chi tiết báo cáo: " + e.getMessage(), e);
        }
    }

    // --- Mock Data Generator ---
    private ReportData mockReportData() {
        ReportData data = new ReportData();
        
        // Summary
        ReportData.Summary summary = new ReportData.Summary();
        summary.setTotalRevenue(125000000);
        summary.setTotalOrders(342);
        summary.setAvgRevenuePerOrder(365497);
        summary.setRevenueChangePercent(12.5);
        data.setSummary(summary);

        // Chart Data
        List<ReportData.ChartData> chartDataList = new ArrayList<>();
        ReportData.ChartData c1 = new ReportData.ChartData(); c1.setLabel("01/2026"); c1.setRevenue(30000000);
        ReportData.ChartData c2 = new ReportData.ChartData(); c2.setLabel("02/2026"); c2.setRevenue(35000000);
        ReportData.ChartData c3 = new ReportData.ChartData(); c3.setLabel("03/2026"); c3.setRevenue(60000000);
        chartDataList.add(c1); chartDataList.add(c2); chartDataList.add(c3);
        data.setChartData(chartDataList);

        // Top Products
        List<ReportData.TopProduct> topProducts = new ArrayList<>();
        ReportData.TopProduct p1 = new ReportData.TopProduct(); p1.setProductName("Bàn phím cơ"); p1.setTotalQuantity(120); p1.setTotalRevenue(102000000);
        ReportData.TopProduct p2 = new ReportData.TopProduct(); p2.setProductName("Chuột không dây"); p2.setTotalQuantity(95); p2.setTotalRevenue(23750000);
        topProducts.add(p1); topProducts.add(p2);
        data.setTopProducts(topProducts);

        return data;
    }

    public void deleteReport(int id) throws ApiException {
        if (AppConfig.IS_MOCK_MODE) {
            return;
        }
        ApiClient.getInstance().delete("/reports/" + id, Void.class);
    }
}

