package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * ReportData: Chứa toàn bộ dữ liệu trả về khi sinh báo cáo mới.
 * Dữ liệu này dùng để hiển thị thẻ số liệu (Dashboard) và vẽ biểu đồ.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class ReportData {

    private Summary summary;
    
    @JsonProperty("chart_data")
    private List<ChartData> chartData;
    
    @JsonProperty("top_products")
    private List<TopProduct> topProducts;

    // Getters and Setters
    public Summary getSummary() { return summary; }
    public void setSummary(Summary summary) { this.summary = summary; }

    public List<ChartData> getChartData() { return chartData; }
    public void setChartData(List<ChartData> chartData) { this.chartData = chartData; }

    public List<TopProduct> getTopProducts() { return topProducts; }
    public void setTopProducts(List<TopProduct> topProducts) { this.topProducts = topProducts; }


    // --- Sub-classes (Nested for convenience, or can be separated) ---

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Summary {
        @JsonProperty("total_revenue")
        private double totalRevenue;
        
        @JsonProperty("total_orders")
        private int totalOrders;
        
        @JsonProperty("avg_revenue_per_order")
        private double avgRevenuePerOrder;
        
        @JsonProperty("revenue_change_percent")
        private double revenueChangePercent;

        // Getters and setters
        public double getTotalRevenue() { return totalRevenue; }
        public void setTotalRevenue(double totalRevenue) { this.totalRevenue = totalRevenue; }

        public int getTotalOrders() { return totalOrders; }
        public void setTotalOrders(int totalOrders) { this.totalOrders = totalOrders; }

        public double getAvgRevenuePerOrder() { return avgRevenuePerOrder; }
        public void setAvgRevenuePerOrder(double avgRevenuePerOrder) { this.avgRevenuePerOrder = avgRevenuePerOrder; }

        public double getRevenueChangePercent() { return revenueChangePercent; }
        public void setRevenueChangePercent(double revenueChangePercent) { this.revenueChangePercent = revenueChangePercent; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ChartData {
        private String label;
        private double revenue;
        
        @JsonProperty("forecast_revenue")
        private Double forecastRevenue;

        // Getters and setters
        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }

        public double getRevenue() { return revenue; }
        public void setRevenue(double revenue) { this.revenue = revenue; }
        
        public Double getForecastRevenue() { return forecastRevenue; }
        public void setForecastRevenue(Double forecastRevenue) { this.forecastRevenue = forecastRevenue; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TopProduct {
        @JsonProperty("product_name")
        private String productName;
        
        @JsonProperty("total_quantity")
        private int totalQuantity;
        
        @JsonProperty("total_revenue")
        private double totalRevenue;

        // Getters and setters
        public String getProductName() { return productName; }
        public void setProductName(String productName) { this.productName = productName; }

        public int getTotalQuantity() { return totalQuantity; }
        public void setTotalQuantity(int totalQuantity) { this.totalQuantity = totalQuantity; }

        public double getTotalRevenue() { return totalRevenue; }
        public void setTotalRevenue(double totalRevenue) { this.totalRevenue = totalRevenue; }
    }



}
