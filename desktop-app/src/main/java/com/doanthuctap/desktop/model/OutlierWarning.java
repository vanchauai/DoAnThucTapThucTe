package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class OutlierWarning {
    private String type;
    
    @JsonProperty("product_name")
    private String productName;
    
    @JsonProperty("actual_value")
    private double actualValue;
    
    @JsonProperty("historical_mean")
    private double historicalMean;
    
    @JsonProperty("z_score")
    private double zScore;
    
    private String message;

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }

    public double getActualValue() { return actualValue; }
    public void setActualValue(double actualValue) { this.actualValue = actualValue; }

    public double getHistoricalMean() { return historicalMean; }
    public void setHistoricalMean(double historicalMean) { this.historicalMean = historicalMean; }

    public double getZScore() { return zScore; }
    public void setZScore(double zScore) { this.zScore = zScore; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
