package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.model.InsightResponse;
import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import com.fasterxml.jackson.core.type.TypeReference;

public class InsightService {

    public InsightResponse getAnswer(String questionId) throws ApiException {
        try {
            String json = ApiClient.getInstance().get("/insights/answer?question_id=" + questionId, String.class);
            return ApiClient.getInstance().getObjectMapper().readValue(json, InsightResponse.class);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Lỗi lấy dữ liệu Trợ lý: " + e.getMessage(), e);
        }
    }
}
