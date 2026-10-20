package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.User;
import com.doanthuctap.desktop.service.UserService;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.Node;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import java.util.Optional;

public class UserManagementController {

    @FXML private TableView<User> tableView;
    @FXML private TableColumn<User, String> colEmail;
    @FXML private TableColumn<User, String> colName;
    @FXML private TableColumn<User, String> colRole;
    @FXML private TableColumn<User, User> colStatus;
    @FXML private TableColumn<User, User> colActions;

    private UserService userService;
    private ObservableList<User> userList = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        userService = new UserService();
        
        // Cấu hình cột Status (dùng badge màu như màn DataSource)
        colStatus.setCellValueFactory(cellData -> new javafx.beans.property.SimpleObjectProperty<>(cellData.getValue()));
        colStatus.setCellFactory(column -> new TableCell<User, User>() {
            @Override
            protected void updateItem(User user, boolean empty) {
                super.updateItem(user, empty);
                if (empty || user == null) {
                    setGraphic(null);
                } else {
                    Label badge = new Label(user.isActive() ? "HOẠT ĐỘNG" : "ĐÃ KHÓA");
                    badge.setStyle("-fx-text-fill: white; -fx-padding: 3 8; -fx-background-radius: 4; -fx-font-size: 11px; -fx-font-weight: bold;");
                    if (user.isActive()) {
                        badge.setStyle(badge.getStyle() + "-fx-background-color: #4CAF50;");
                    } else {
                        badge.setStyle(badge.getStyle() + "-fx-background-color: #F44336;");
                    }
                    setGraphic(badge);
                    setAlignment(Pos.CENTER);
                }
            }
        });

        // Cấu hình cột Actions (2 nút Sửa và Khóa/Mở)
        colActions.setCellValueFactory(cellData -> new javafx.beans.property.SimpleObjectProperty<>(cellData.getValue()));
        colActions.setCellFactory(column -> new TableCell<User, User>() {
            @Override
            protected void updateItem(User user, boolean empty) {
                super.updateItem(user, empty);
                if (empty || user == null) {
                    setGraphic(null);
                } else {
                    Button btnEdit = new Button("Sửa");
                    btnEdit.setStyle("-fx-background-color: #FFA000; -fx-text-fill: white; -fx-cursor: hand; -fx-font-size: 12px; -fx-padding: 4 8;");
                    btnEdit.setOnAction(e -> showUserDialog(user));

                    Button btnToggle = new Button(user.isActive() ? "Khóa" : "Mở khóa");
                    btnToggle.setStyle("-fx-background-color: " + (user.isActive() ? "#D32F2F" : "#388E3C") + "; -fx-text-fill: white; -fx-cursor: hand; -fx-font-size: 12px; -fx-padding: 4 8;");
                    btnToggle.setOnAction(e -> handleToggleStatus(user));

                    HBox hbox = new HBox(10, btnEdit, btnToggle);
                    hbox.setAlignment(Pos.CENTER);
                    setGraphic(hbox);
                }
            }
        });

        tableView.setItems(userList);
        loadData();
    }

    private void loadData() {
        new Thread(() -> {
            try {
                var users = userService.getUsers();
                Platform.runLater(() -> {
                    userList.clear();
                    userList.addAll(users);
                });
            } catch (Exception e) {
                Platform.runLater(() -> UIUtils.showError("Lỗi tải danh sách", e.getMessage()));
            }
        }).start();
    }

    @FXML
    private void handleAddUser() {
        showUserDialog(null);
    }

    private void showUserDialog(User existingUser) {
        boolean isEdit = existingUser != null;
        Dialog<User> dialog = new Dialog<>();
        dialog.setTitle(isEdit ? "Sửa người dùng" : "Thêm người dùng");
        dialog.setHeaderText(isEdit ? "Cập nhật thông tin tài khoản" : "Nhập thông tin tài khoản mới");

        ButtonType btnSaveType = new ButtonType("Lưu", ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(btnSaveType, ButtonType.CANCEL);

        GridPane grid = new GridPane();
        grid.setHgap(10); grid.setVgap(10); grid.setPadding(new Insets(20, 50, 10, 10));

        TextField txtEmail = new TextField();
        txtEmail.setPromptText("Email");
        PasswordField txtPassword = new PasswordField();
        txtPassword.setPromptText(isEdit ? "Bỏ trống nếu không đổi" : "Mật khẩu");
        TextField txtName = new TextField();
        txtName.setPromptText("Họ và tên");
        
        ComboBox<String> cbRole = new ComboBox<>(FXCollections.observableArrayList("admin", "manager", "employee"));
        cbRole.setValue("employee");

        dialog.getDialogPane().setContent(grid);

        // Validate cơ bản
        Node btnSave = dialog.getDialogPane().lookupButton(btnSaveType);
        btnSave.setDisable(!isEdit);
        txtEmail.textProperty().addListener((obs, oldV, newV) -> btnSave.setDisable(newV.trim().isEmpty()));
        if (!isEdit) {
            txtPassword.textProperty().addListener((obs, oldV, newV) -> btnSave.setDisable(newV.trim().isEmpty() || txtEmail.getText().trim().isEmpty()));
        }

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == btnSaveType) {
                User user = new User();
                user.setEmail(txtEmail.getText().trim());
                user.setFullName(txtName.getText().trim());
                user.setRole(cbRole.getValue());
                return user;
            }
            return null;
        });

        Optional<User> result = dialog.showAndWait();
        result.ifPresent(user -> {
            new Thread(() -> {
                try {
                    if (isEdit) {
                        userService.updateUser(existingUser.getId(), user, txtPassword.getText());
                    } else {
                        userService.createUser(user, txtPassword.getText());
                    }
                    Platform.runLater(() -> {
                        UIUtils.showInfo("Thành công", isEdit ? "Cập nhật thành công!" : "Thêm mới thành công!");
                        loadData();
                    });
                } catch (Exception e) {
                    Platform.runLater(() -> UIUtils.showError("Lỗi", e.getMessage()));
                }
            }).start();
        });
    }

    private void handleToggleStatus(User user) {
        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
        confirm.setTitle("Xác nhận");
        confirm.setHeaderText(user.isActive() ? "Khóa tài khoản" : "Mở khóa tài khoản");
        confirm.setContentText("Bạn có chắc chắn muốn " + (user.isActive() ? "khóa" : "mở khóa") + " tài khoản " + user.getEmail() + " không?");
        
        Optional<ButtonType> result = confirm.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            new Thread(() -> {
                try {
                    userService.toggleUserStatus(user.getId(), !user.isActive());
                    Platform.runLater(() -> {
                        UIUtils.showInfo("Thành công", "Đã cập nhật trạng thái!");
                        loadData();
                    });
                } catch (Exception e) {
                    Platform.runLater(() -> UIUtils.showError("Lỗi", e.getMessage()));
                }
            }).start();
        }
    }
}

