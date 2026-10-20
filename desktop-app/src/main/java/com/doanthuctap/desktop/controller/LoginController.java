package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.App;
import com.doanthuctap.desktop.service.AuthService;
import com.doanthuctap.desktop.network.ApiException;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;

import javafx.scene.shape.SVGPath;
import java.io.IOException;

/**
 * LoginController: Điều khiển màn hình đăng nhập.
 * Nhận email/password từ giao diện và gọi AuthService.
 */
public class LoginController {

    @FXML private TextField emailField;
    @FXML private PasswordField passwordField;
    @FXML private TextField passwordTextField;
    @FXML private Button togglePasswordBtn;
    @FXML private SVGPath eyeIcon;
    @FXML private Button loginButton;
    @FXML private VBox loadingBox; 

    private AuthService authService;
    private boolean isPasswordVisible = false;

    @FXML
    public void initialize() {
        authService = new AuthService();
        loadingBox.setVisible(false);

        // Bind the text properties so they stay in sync
        if (passwordTextField != null && passwordField != null) {
            passwordTextField.textProperty().bindBidirectional(passwordField.textProperty());
        }
    }

    @FXML
    private void togglePasswordVisible() {
        isPasswordVisible = !isPasswordVisible;
        if (isPasswordVisible) {
            passwordTextField.setVisible(true);
            passwordField.setVisible(false);
            if (eyeIcon != null) {
                // Eye slashed
                eyeIcon.setContent("M12,7 C14.76,7 17,9.24 17,12 C17,12.29 16.97,12.57 16.91,12.84 L19.46,15.39 C20.91,14.47 22.1,13.34 23,12 C21.27,7.61 17,4.5 12,4.5 C10.6,4.5 9.26,4.75 8,5.2 L10.15,7.35 C10.73,7.12 11.35,7 12,7 Z M2.71,3.16 L1.29,4.58 L3.57,6.86 C2.4,8.32 1.54,9.99 1,12 C2.73,16.39 7,19.5 12,19.5 C14.16,19.5 16.19,19.04 17.98,18.23 L20.42,20.67 L21.84,19.25 L2.71,3.16 Z M9,12.28 L11.72,15 C11.81,15 11.9,15 12,15 C13.66,15 15,13.66 15,12 C15,11.9 15,11.81 15,11.72 L12.28,9 C12.19,9 12.09,9 12,9 C10.34,9 9,10.34 9,12 C9,12.09 9,12.19 9,12.28 Z");
            }
        } else {
            passwordTextField.setVisible(false);
            passwordField.setVisible(true);
            if (eyeIcon != null) {
                // Eye open
                eyeIcon.setContent("M12,4.5 C7,4.5 2.73,7.61 1,12 C2.73,16.39 7,19.5 12,19.5 C17,19.5 21.27,16.39 23,12 C21.27,7.61 17,4.5 12,4.5 Z M12,17 C9.24,17 7,14.76 7,12 C7,9.24 9.24,7 12,7 C14.76,7 17,9.24 17,12 C17,14.76 14.76,17 12,17 Z M12,9 C10.34,9 9,10.34 9,12 C9,13.66 10.34,15 12,15 C13.66,15 15,13.66 15,12 C15,10.34 13.66,9 12,9 Z");
            }
        }
    }

    @FXML
    private void handleForgetPassword() {
        UIUtils.showInfo("Quên mật khẩu", "Chức năng quên mật khẩu đang được phát triển.");
    }

    @FXML
    private void handleRegister() {
        UIUtils.showInfo("Đăng ký", "Chức năng đăng ký đang được phát triển.");
        // Có thể thêm navigation sang màn hình register ở đây
    }

    @FXML
    private void handleLogin() {
        String email = emailField.getText();
        String pass = passwordField.getText();

        if (email == null || email.isEmpty() || pass == null || pass.isEmpty()) {
            UIUtils.showError("Lỗi nhập liệu", "Vui lòng nhập đầy đủ Email và Mật khẩu.");
            return;
        }

        loginButton.setDisable(true);
        loadingBox.setVisible(true);

        new Thread(() -> {
            try {
                authService.login(email, pass);
                Platform.runLater(() -> {
                    try {
                        App.setRoot("main", "SmartSyncVN", 1200, 800);
                    } catch (IOException e) {
                        UIUtils.showError("Lỗi giao diện", "Không thể tải giao diện chính.");
                    }
                });
            } catch (ApiException e) {
                Platform.runLater(() -> {
                    UIUtils.showError("Đăng nhập thất bại", e.getMessage());
                    loginButton.setDisable(false);
                    loadingBox.setVisible(false);
                });
            }
        }).start();
    }
}
