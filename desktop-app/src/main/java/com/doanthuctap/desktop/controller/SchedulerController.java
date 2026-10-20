package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.network.ApiException;
import com.doanthuctap.desktop.service.SchedulerService;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.Button;

public class SchedulerController {

    @FXML private Spinner<Integer> spHour;
    @FXML private Spinner<Integer> spMinute;
    @FXML private Button btnSave;

    private SchedulerService schedulerService;

    @FXML
    public void initialize() {
        schedulerService = new SchedulerService();
        
        // Cấu hình Spinner Giờ (0-23)
        spHour.setValueFactory(new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 23, 18));
        // Cấu hình Spinner Phút (0-59)
        spMinute.setValueFactory(new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 59, 0));
    }

    @FXML
    private void handleSaveConfig() {
        int hour = spHour.getValue();
        int minute = spMinute.getValue();
        
        btnSave.setDisable(true);
        new Thread(() -> {
            try {
                schedulerService.configScheduler(hour, minute);
                Platform.runLater(() -> {
                    UIUtils.showInfo("Thành công", "Đã cập nhật lịch báo cáo hàng ngày thành " + hour + ":" + String.format("%02d", minute));
                    btnSave.setDisable(false);
                });
            } catch (ApiException e) {
                Platform.runLater(() -> {
                    UIUtils.showError("Lỗi cấu hình lịch", e.getMessage());
                    btnSave.setDisable(false);
                });
            }
        }).start();
    }
}
