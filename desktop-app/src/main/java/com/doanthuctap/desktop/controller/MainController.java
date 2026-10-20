package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.App;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.layout.BorderPane;

import java.io.IOException;

/**
 * MainController: Quản lý layout chính, bao gồm sidebar (thanh điều hướng)
 * và contentArea (khu vực hiển thị nội dung tùy theo menu được chọn).
 */
public class MainController {

    @FXML private BorderPane mainLayout;
    @FXML private javafx.scene.control.Button btnScheduler;
    @FXML private javafx.scene.control.Button btnUsers;

    @FXML private javafx.scene.control.Label lblTopHello;
    @FXML private javafx.scene.control.Label lblTopAvatarLetter;

    private static MainController instance;

    public MainController() {
        instance = this;
    }

    public static MainController getInstance() {
        return instance;
    }

    public void navigateToDataSource() {
        showDataSource();
    }

    @FXML
    public void initialize() {
        loadView("dashboard");
        
        com.doanthuctap.desktop.model.User user = com.doanthuctap.desktop.session.UserSession.getInstance().getUser();
        if (user != null) {
            String roleStr = "Nhân viên";
            if ("admin".equalsIgnoreCase(user.getRole())) {
                roleStr = "Quản trị viên";
            } else if ("manager".equalsIgnoreCase(user.getRole())) {
                roleStr = "Quản lý";
            }
            
            if (lblTopHello != null) {
                lblTopHello.setText("Hello " + roleStr);
            }
            if (lblTopAvatarLetter != null && roleStr.length() > 0) {
                lblTopAvatarLetter.setText(String.valueOf(roleStr.charAt(0)).toUpperCase());
            }

            if (!"admin".equalsIgnoreCase(user.getRole())) {
                if (btnScheduler != null) {
                    btnScheduler.setVisible(false);
                    btnScheduler.setManaged(false);
                }
                if (btnUsers != null) {
                    btnUsers.setVisible(false);
                    btnUsers.setManaged(false);
                }
            }
        }
    }

    @FXML
    private void showDashboard() {
        loadView("dashboard");
    }

    @FXML
    private void showDataSource() {
        loadView("data_source");
    }

    @FXML
    private void showReport() {
        loadView("report");
    }

    @FXML
    private void showPrediction() {
        loadView("prediction");
    }

    @FXML
    private void showDataAssistant() {
        loadView("assistant");
    }

    @FXML
    private void showScheduler() {
        loadView("scheduler");
    }
    
    @FXML
    private void showUsers() {
        loadView("user_management");
    }
    
    @FXML
    private void showChangePassword() {
        javafx.scene.control.Dialog<Void> dialog = new javafx.scene.control.Dialog<>();
        dialog.setTitle("Đổi mật khẩu");
        dialog.setHeaderText("Nhập thông tin để đổi mật khẩu của bạn");
        
        javafx.scene.control.ButtonType btnSaveType = new javafx.scene.control.ButtonType("Lưu thay đổi", javafx.scene.control.ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(btnSaveType, javafx.scene.control.ButtonType.CANCEL);
        
        javafx.scene.layout.GridPane grid = new javafx.scene.layout.GridPane();
        grid.setHgap(10); grid.setVgap(10); grid.setPadding(new javafx.geometry.Insets(20, 150, 10, 10));
        
        javafx.scene.control.PasswordField txtOld = new javafx.scene.control.PasswordField();
        javafx.scene.control.PasswordField txtNew = new javafx.scene.control.PasswordField();
        javafx.scene.control.PasswordField txtConfirm = new javafx.scene.control.PasswordField();
        
        grid.add(new javafx.scene.control.Label("Mật khẩu cũ:"), 0, 0); grid.add(txtOld, 1, 0);
        grid.add(new javafx.scene.control.Label("Mật khẩu mới:"), 0, 1); grid.add(txtNew, 1, 1);
        grid.add(new javafx.scene.control.Label("Xác nhận MK:"), 0, 2); grid.add(txtConfirm, 1, 2);
        
        dialog.getDialogPane().setContent(grid);
        
        // Validate
        javafx.scene.Node btnSave = dialog.getDialogPane().lookupButton(btnSaveType);
        btnSave.setDisable(true);
        javafx.beans.value.ChangeListener<String> listener = (obs, oldV, newV) -> {
            btnSave.setDisable(txtOld.getText().trim().isEmpty() || txtNew.getText().trim().isEmpty() || !txtNew.getText().equals(txtConfirm.getText()));
        };
        txtOld.textProperty().addListener(listener); txtNew.textProperty().addListener(listener); txtConfirm.textProperty().addListener(listener);
        
        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == btnSaveType) {
                new Thread(() -> {
                    try {
                        new com.doanthuctap.desktop.service.UserService().changeMyPassword(txtOld.getText(), txtNew.getText());
                        javafx.application.Platform.runLater(() -> com.doanthuctap.desktop.util.UIUtils.showInfo("Thành công", "Đổi mật khẩu thành công!"));
                    } catch (Exception e) {
                        javafx.application.Platform.runLater(() -> com.doanthuctap.desktop.util.UIUtils.showError("Lỗi", e.getMessage()));
                    }
                }).start();
            }
            return null;
        });
        
        dialog.showAndWait();
    }

    @FXML
    private void handleLogout() {
        try {
            App.setRoot("login", "Đăng nhập hệ thống", 950, 650);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void loadView(String fxmlFile) {
        try {
            FXMLLoader loader = new FXMLLoader(App.class.getResource("/fxml/" + fxmlFile + ".fxml"));
            Node view = loader.load();
            mainLayout.setCenter(view);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
