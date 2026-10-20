package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.User;
import com.doanthuctap.desktop.session.UserSession;
import javafx.fxml.FXML;
import javafx.scene.control.Label;

public class DashboardController {

    @FXML private Label lblGreeting;
    @FXML private Label lblRoleBadge;

    private User currentUser;

    @FXML
    public void initialize() {
        currentUser = UserSession.getInstance().getUser();
        if (currentUser != null) {
            lblGreeting.setText("Chào buổi sáng, " + currentUser.getFullName());
            
            String roleStr = "Nhân viên";
            if ("admin".equalsIgnoreCase(currentUser.getRole())) {
                roleStr = "Quản trị viên";
            } else if ("manager".equalsIgnoreCase(currentUser.getRole())) {
                roleStr = "Quản lý";
            }
            lblRoleBadge.setText(roleStr);
        }
    }

    @FXML
    private void handleDiscover() {
        MainController.getInstance().navigateToDataSource();
    }
}

