package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * ListResponse: Model generic để bọc danh sách dữ liệu và tổng số (total) trả về từ API.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class ListResponse<T> {
    private List<T> data;
    private int total;

    public List<T> getData() { return data; }
    public void setData(List<T> data) { this.data = data; }

    public int getTotal() { return total; }
    public void setTotal(int total) { this.total = total; }
}
