package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.DataSource;
import com.doanthuctap.desktop.model.ListResponse;
import com.doanthuctap.desktop.network.ApiException;
import com.doanthuctap.desktop.service.DataSourceService;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.File;

/**
 * DataSourceController: Quản lý màn hình Nguồn dữ liệu.
 */
public class DataSourceController {

    @FXML private TableView<DataSource> tableView;
    @FXML private TableColumn<DataSource, Integer> colId;
    @FXML private TableColumn<DataSource, String> colName;
    @FXML private TableColumn<DataSource, String> colType;
    @FXML private TableColumn<DataSource, String> colStatus;
    @FXML private TableColumn<DataSource, String> colLastSync;

    @FXML private Button btnUpload;
    @FXML private Button btnConnectGSheets;
    @FXML private Button btnSync;
    @FXML private Button btnDelete;

    private DataSourceService dataSourceService;
    private ObservableList<DataSource> dataList = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        dataSourceService = new DataSourceService();
        setupTable();
        loadData();
    }

    private void setupTable() {
        colId.setCellValueFactory(new PropertyValueFactory<>("id"));
        colName.setCellValueFactory(new PropertyValueFactory<>("name"));
        colType.setCellValueFactory(new PropertyValueFactory<>("type"));
        colStatus.setCellValueFactory(new PropertyValueFactory<>("status"));
        colStatus.setCellFactory(column -> new javafx.scene.control.TableCell<DataSource, String>() {
            private final javafx.scene.control.Label badge = new javafx.scene.control.Label();
            
            {
                setAlignment(javafx.geometry.Pos.CENTER_LEFT);
            }

            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setGraphic(null);
                    setText(null);
                } else {
                    badge.setText(item.toUpperCase());
                    String baseStyle = "-fx-padding: 4 12; -fx-background-radius: 4; -fx-text-fill: white; -fx-font-weight: bold; -fx-font-size: 11px;";
                    if (item.toLowerCase().contains("sync")) {
                        badge.setStyle(baseStyle + " -fx-background-color: #4CAF50;"); // Xanh lá
                    } else if (item.toLowerCase().contains("error") || item.toLowerCase().contains("lỗi")) {
                        badge.setStyle(baseStyle + " -fx-background-color: #F44336;"); // Đỏ
                    } else {
                        badge.setStyle(baseStyle + " -fx-background-color: #9E9E9E;"); // Xám cho các trạng thái khác
                    }
                    setGraphic(badge);
                    setText(null);
                }
            }
        });
        colLastSync.setCellValueFactory(new PropertyValueFactory<>("lastSyncedAt"));
        tableView.setItems(dataList);
        
        // Bật nút Sync và Delete chỉ khi chọn 1 dòng
        tableView.getSelectionModel().selectedItemProperty().addListener((obs, oldSel, newSel) -> {
            boolean disable = (newSel == null);
            btnSync.setDisable(disable);
            btnDelete.setDisable(disable);
        });
        btnSync.setDisable(true);
        btnDelete.setDisable(true);
    }

    private void loadData() {
        new Thread(() -> {
            try {
                ListResponse<DataSource> response = dataSourceService.getDataSources();
                Platform.runLater(() -> {
                    dataList.clear();
                    if (response.getData() != null) {
                        dataList.addAll(response.getData());
                    }
                });
            } catch (ApiException e) {
                Platform.runLater(() -> UIUtils.showError("Lỗi tải nguồn dữ liệu", e.getMessage()));
            }
        }).start();
    }

    @FXML
    private void handleUpload() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Chọn file Excel/CSV");
        fileChooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("Excel/CSV Files", "*.xlsx", "*.xls", "*.csv")
        );
        File file = fileChooser.showOpenDialog(new Stage());
        if (file != null) {
            btnUpload.setDisable(true);
            new Thread(() -> {
                try {
                    DataSource uploaded = dataSourceService.uploadExcel(file, file.getName());
                    if (uploaded != null && uploaded.getId() > 0) {
                        com.doanthuctap.desktop.model.SyncResponse syncRes = dataSourceService.syncDataSource(uploaded.getId());
                        Platform.runLater(() -> {
                            UIUtils.showInfo("Thành công", "Đã tải lên và đồng bộ dữ liệu thành công từ file: " + file.getName());
                            processSyncResult(syncRes);
                            loadData();
                            btnUpload.setDisable(false);
                        });
                    } else {
                        Platform.runLater(() -> {
                            loadData();
                            btnUpload.setDisable(false);
                        });
                    }
                } catch (ApiException e) {
                    Platform.runLater(() -> {
                        UIUtils.showError("Lỗi tải lên", e.getMessage());
                        loadData();
                        btnUpload.setDisable(false);
                    });
                }
            }).start();
        }
    }

    @FXML
    private void handleConnectGSheets() {
        btnConnectGSheets.setDisable(true);
        new Thread(() -> {
            try {
                String email = dataSourceService.getServiceAccountEmail();
                Platform.runLater(() -> {
                    btnConnectGSheets.setDisable(false);
                    showGSheetsDialog(email);
                });
            } catch (ApiException e) {
                Platform.runLater(() -> {
                    btnConnectGSheets.setDisable(false);
                    UIUtils.showError("Lỗi kết nối", "Không thể lấy email Service Account: " + e.getMessage());
                });
            }
        }).start();
    }

    private void showGSheetsDialog(String email) {
        javafx.scene.control.Dialog<javafx.util.Pair<String, String>> dialog = new javafx.scene.control.Dialog<>();
        dialog.setTitle("Kết nối Google Sheets");
        dialog.setHeaderText("Thêm nguồn dữ liệu từ Google Sheets");

        javafx.scene.control.ButtonType connectButtonType = new javafx.scene.control.ButtonType("Kết nối", javafx.scene.control.ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().addAll(connectButtonType, javafx.scene.control.ButtonType.CANCEL);

        javafx.scene.layout.GridPane grid = new javafx.scene.layout.GridPane();
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setPadding(new javafx.geometry.Insets(20, 150, 10, 10));

        javafx.scene.control.Label lblEmail = new javafx.scene.control.Label("Bước 1: Chia sẻ Google Sheet của bạn với email sau (quyền Viewer):\n" + email);
        lblEmail.setWrapText(true);
        javafx.scene.control.Button btnCopy = new javafx.scene.control.Button("Copy");
        btnCopy.setOnAction(e -> {
            javafx.scene.input.Clipboard clipboard = javafx.scene.input.Clipboard.getSystemClipboard();
            javafx.scene.input.ClipboardContent content = new javafx.scene.input.ClipboardContent();
            content.putString(email);
            clipboard.setContent(content);
        });

        javafx.scene.layout.HBox emailBox = new javafx.scene.layout.HBox(10, lblEmail, btnCopy);
        grid.add(emailBox, 0, 0, 2, 1);

        javafx.scene.control.TextField urlField = new javafx.scene.control.TextField();
        urlField.setPromptText("https://docs.google.com/spreadsheets/d/...");
        javafx.scene.control.TextField nameField = new javafx.scene.control.TextField();
        nameField.setPromptText("Ví dụ: Doanh thu Q3");

        grid.add(new javafx.scene.control.Label("URL Google Sheet:"), 0, 1);
        grid.add(urlField, 1, 1);
        grid.add(new javafx.scene.control.Label("Tên gợi nhớ:"), 0, 2);
        grid.add(nameField, 1, 2);

        javafx.scene.Node connectButton = dialog.getDialogPane().lookupButton(connectButtonType);
        connectButton.setDisable(true);

        urlField.textProperty().addListener((observable, oldValue, newValue) -> {
            connectButton.setDisable(newValue.trim().isEmpty() || nameField.getText().trim().isEmpty());
        });
        nameField.textProperty().addListener((observable, oldValue, newValue) -> {
            connectButton.setDisable(newValue.trim().isEmpty() || urlField.getText().trim().isEmpty());
        });

        dialog.getDialogPane().setContent(grid);
        Platform.runLater(urlField::requestFocus);

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == connectButtonType) {
                return new javafx.util.Pair<>(urlField.getText().trim(), nameField.getText().trim());
            }
            return null;
        });

        dialog.showAndWait().ifPresent(result -> {
            String url = result.getKey();
            String name = result.getValue();
            
            btnConnectGSheets.setDisable(true);
            new Thread(() -> {
                try {
                    DataSource created = dataSourceService.createGSheetsSource(name, url);
                    if (created != null && created.getId() > 0) {
                        com.doanthuctap.desktop.model.SyncResponse syncRes = dataSourceService.syncDataSource(created.getId());
                        Platform.runLater(() -> {
                            UIUtils.showInfo("Thành công", "Đã kết nối và đồng bộ dữ liệu Google Sheets thành công!");
                            processSyncResult(syncRes);
                            loadData();
                            btnConnectGSheets.setDisable(false);
                        });
                    }
                } catch (ApiException ex) {
                    Platform.runLater(() -> {
                        UIUtils.showError("Lỗi kết nối", ex.getMessage());
                        loadData();
                        btnConnectGSheets.setDisable(false);
                    });
                }
            }).start();
        });
    }

    @FXML
    private void handleSync() {
        DataSource selected = tableView.getSelectionModel().getSelectedItem();
        if (selected == null) return;
        
        btnSync.setDisable(true);
        new Thread(() -> {
            try {
                com.doanthuctap.desktop.model.SyncResponse syncRes = dataSourceService.syncDataSource(selected.getId());
                Platform.runLater(() -> {
                    UIUtils.showInfo("Đồng bộ", "Đã gửi yêu cầu đồng bộ thành công!");
                    processSyncResult(syncRes);
                    loadData();
                    btnSync.setDisable(false);
                });
            } catch (ApiException e) {
                Platform.runLater(() -> {
                    UIUtils.showError("Đồng bộ thất bại", e.getMessage());
                    btnSync.setDisable(false);
                });
            }
        }).start();
    }

    @FXML
    private void handleDelete() {
        DataSource selected = tableView.getSelectionModel().getSelectedItem();
        if (selected == null) return;
        
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(javafx.scene.control.Alert.AlertType.CONFIRMATION);
        alert.setTitle("Xác nhận xóa");
        alert.setHeaderText("Bạn có chắc chắn muốn xóa nguồn dữ liệu này?");
        alert.setContentText("Nguồn dữ liệu: " + selected.getName());
        
        if (alert.showAndWait().orElse(javafx.scene.control.ButtonType.CANCEL) == javafx.scene.control.ButtonType.OK) {
            btnDelete.setDisable(true);
            new Thread(() -> {
                try {
                    dataSourceService.deleteDataSource(selected.getId());
                    Platform.runLater(() -> {
                        UIUtils.showInfo("Thành công", "Đã xóa nguồn dữ liệu!");
                        loadData();
                    });
                } catch (ApiException e) {
                    Platform.runLater(() -> {
                        UIUtils.showError("Lỗi khi xóa", e.getMessage());
                        btnDelete.setDisable(false);
                    });
                }
            }).start();
        }
    }
    
    private void processSyncResult(com.doanthuctap.desktop.model.SyncResponse response) {
        if (response == null) return;
        
        StringBuilder sb = new StringBuilder();
        boolean hasWarning = false;
        
        if (response.getRowWarnings() != null && !response.getRowWarnings().isEmpty()) {
            sb.append(String.format("Đã đồng bộ %d/%d dòng thành công. %d dòng bị bỏ qua do lỗi dữ liệu, xem chi tiết bên dưới.\n\n", 
                    response.getTotalRowsSuccess(), response.getTotalRowsProcessed(), response.getRowWarnings().size()));
            sb.append("--- CHI TIẾT LỖI TỪNG DÒNG ---\n");
            for (String w : response.getRowWarnings()) {
                sb.append("- ").append(w).append("\n");
            }
            sb.append("\n");
            hasWarning = true;
        }
        
        if (response.getCrossFileWarnings() != null && !response.getCrossFileWarnings().isEmpty()) {
            sb.append("--- CẢNH BÁO DỮ LIỆU LIÊN KẾT ---\n");
            for (String w : response.getCrossFileWarnings()) {
                sb.append("- ").append(w).append("\n");
            }
            sb.append("\n");
            hasWarning = true;
        }
        
        if (response.getOutlierWarnings() != null && !response.getOutlierWarnings().isEmpty()) {
            sb.append("--- CẢNH BÁO OUTLIER (Bất thường lịch sử) ---\n");
            for (com.doanthuctap.desktop.model.OutlierWarning w : response.getOutlierWarnings()) {
                sb.append("- ").append(w.getMessage()).append("\n");
            }
            hasWarning = true;
        }
        
        if (hasWarning) {
            UIUtils.showWarning("Phát hiện vấn đề dữ liệu", sb.toString());
        }
    }
}
