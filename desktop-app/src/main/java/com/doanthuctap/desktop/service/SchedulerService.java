package com.doanthuctap.desktop.service;

import com.doanthuctap.desktop.network.ApiClient;
import com.doanthuctap.desktop.network.ApiException;
import java.util.HashMap;
import java.util.Map;

public class SchedulerService {
    
    public void configScheduler(int hour, int minute) throws ApiException {
        Map<String, Object> body = new HashMap<>();
        body.put("daily_report_hour", hour);
        body.put("daily_report_minute", minute);
        
        ApiClient.getInstance().post("/scheduler/config", body, String.class);
    }
}
