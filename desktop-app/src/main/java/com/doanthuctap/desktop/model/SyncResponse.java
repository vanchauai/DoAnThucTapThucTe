package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class SyncResponse {
    private String message;
    
    @JsonProperty("total_synced")
    private int totalSynced;
    
    @JsonProperty("total_errors")
    private int totalErrors;
    
    @JsonProperty("cross_file_warnings")
    private List<String> crossFileWarnings;
    
    @JsonProperty("outlier_warnings")
    private List<OutlierWarning> outlierWarnings;
    @JsonProperty("total_rows_processed")
    private int totalRowsProcessed;
    
    @JsonProperty("total_rows_success")
    private int totalRowsSuccess;
    
    @JsonProperty("row_warnings")
    private List<String> rowWarnings;

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public int getTotalSynced() { return totalSynced; }
    public void setTotalSynced(int totalSynced) { this.totalSynced = totalSynced; }

    public int getTotalErrors() { return totalErrors; }
    public void setTotalErrors(int totalErrors) { this.totalErrors = totalErrors; }
    
    public int getTotalRowsProcessed() { return totalRowsProcessed; }
    public void setTotalRowsProcessed(int totalRowsProcessed) { this.totalRowsProcessed = totalRowsProcessed; }
    
    public int getTotalRowsSuccess() { return totalRowsSuccess; }
    public void setTotalRowsSuccess(int totalRowsSuccess) { this.totalRowsSuccess = totalRowsSuccess; }
    
    public List<String> getRowWarnings() { return rowWarnings; }
    public void setRowWarnings(List<String> rowWarnings) { this.rowWarnings = rowWarnings; }

    public List<String> getCrossFileWarnings() { return crossFileWarnings; }
    public void setCrossFileWarnings(List<String> crossFileWarnings) { this.crossFileWarnings = crossFileWarnings; }

    public List<OutlierWarning> getOutlierWarnings() { return outlierWarnings; }
    public void setOutlierWarnings(List<OutlierWarning> outlierWarnings) { this.outlierWarnings = outlierWarnings; }
}
