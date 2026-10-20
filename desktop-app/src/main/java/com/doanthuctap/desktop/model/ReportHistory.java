package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * ReportHistory: Đại diện cho lịch sử báo cáo trả về từ API `/reports/history`.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class ReportHistory {
    private int id;
    
    @JsonProperty("report_name")
    private String reportName;
    
    @JsonProperty("period_type")
    private String periodType;
    
    @JsonProperty("period_value")
    private String periodValue;
    
    @JsonProperty("created_by")
    private int createdBy;
    
    @JsonProperty("created_at")
    private String createdAt;
    
    @JsonProperty("file_url_excel")
    private String fileUrlExcel;
    
    @JsonProperty("file_url_pdf")
    private String fileUrlPdf;

    // Getters and Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getReportName() { return reportName; }
    public void setReportName(String reportName) { this.reportName = reportName; }

    public String getPeriodType() { return periodType; }
    public void setPeriodType(String periodType) { this.periodType = periodType; }

    public String getPeriodValue() { return periodValue; }
    public void setPeriodValue(String periodValue) { this.periodValue = periodValue; }

    public int getCreatedBy() { return createdBy; }
    public void setCreatedBy(int createdBy) { this.createdBy = createdBy; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getFileUrlExcel() { return fileUrlExcel; }
    public void setFileUrlExcel(String fileUrlExcel) { this.fileUrlExcel = fileUrlExcel; }

    public String getFileUrlPdf() { return fileUrlPdf; }
    public void setFileUrlPdf(String fileUrlPdf) { this.fileUrlPdf = fileUrlPdf; }
}

