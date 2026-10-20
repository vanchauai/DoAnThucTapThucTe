package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.ListResponse;
import com.doanthuctap.desktop.model.ReportHistory;
import com.doanthuctap.desktop.network.ApiException;
import com.doanthuctap.desktop.service.ReportService;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.input.MouseButton;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Modality;
import javafx.stage.Stage;
import com.doanthuctap.desktop.model.ReportData;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * ReportController: Quản lý màn hình Báo cáo (Hiển thị lịch sử báo cáo).
 */
public class ReportController {

    @FXML private ComboBox<String> cbPeriod;
    @FXML private TextField txtPeriodValue;
    
    @FXML private TableView<ReportHistory> tableView;
    @FXML private TableColumn<ReportHistory, Integer> colId;
    @FXML private TableColumn<ReportHistory, String> colName;
    @FXML private TableColumn<ReportHistory, String> colPeriod;
    @FXML private TableColumn<ReportHistory, String> colCreatedAt;

    @FXML private Button btnDelete;
    @FXML private Button btnViewDetail;

    private ReportService reportService;
    private ObservableList<ReportHistory> dataList = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        reportService = new ReportService();
        
        // Khởi tạo ComboBox
        cbPeriod.setItems(FXCollections.observableArrayList("Theo tháng", "Theo quý", "Theo năm"));
        
        // Listener thay đổi prompt
        cbPeriod.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal == null) return;
            if (newVal.equals("Theo tháng")) {
                txtPeriodValue.setPromptText("VD: " + LocalDate.now().format(DateTimeFormatter.ofPattern("MM/yyyy")));
            } else if (newVal.equals("Theo quý")) {
                txtPeriodValue.setPromptText("VD: Q3/2026");
            } else if (newVal.equals("Theo năm")) {
                txtPeriodValue.setPromptText("VD: " + LocalDate.now().getYear());
            }
        });
        cbPeriod.getSelectionModel().selectFirst();

        setupTable();
        loadHistory();
    }

    private void setupTable() {
        colId.setCellValueFactory(new PropertyValueFactory<>("id"));
        colName.setCellValueFactory(new PropertyValueFactory<>("reportName"));
        colPeriod.setCellValueFactory(new PropertyValueFactory<>("periodValue"));
        colCreatedAt.setCellValueFactory(new PropertyValueFactory<>("createdAt"));
        
        tableView.setItems(dataList);
        
        tableView.getSelectionModel().selectedItemProperty().addListener((obs, oldSel, newSel) -> {
            boolean disable = (newSel == null);
            if (btnDelete != null) btnDelete.setDisable(disable);
            if (btnViewDetail != null) btnViewDetail.setDisable(disable);
        });
        
        // Bắt sự kiện double-click
        tableView.setRowFactory(tv -> {
            TableRow<ReportHistory> row = new TableRow<>();
            row.setOnMouseClicked(event -> {
                if (!row.isEmpty() && event.getButton() == MouseButton.PRIMARY && event.getClickCount() == 2) {
                    ReportHistory clickedRow = row.getItem();
                    openReportDetail(clickedRow.getId());
                }
            });
            return row;
        });
    }

    private void loadHistory() {
        new Thread(() -> {
            try {
                ListResponse<ReportHistory> response = reportService.getHistory();
                Platform.runLater(() -> {
                    dataList.clear();
                    if (response.getData() != null) {
                        dataList.addAll(response.getData());
                    }
                });
            } catch (ApiException e) {
                Platform.runLater(() -> UIUtils.showError("Lỗi tải lịch sử báo cáo", e.getMessage()));
            }
        }).start();
    }

    @FXML
    private void handleDelete() {
        ReportHistory selected = tableView.getSelectionModel().getSelectedItem();
        if (selected == null) return;
        
        javafx.scene.control.Alert alert = new javafx.scene.control.Alert(javafx.scene.control.Alert.AlertType.CONFIRMATION);
        alert.setTitle("Xác nhận xóa");
        alert.setHeaderText("Bạn có chắc chắn muốn xóa báo cáo này?");
        alert.setContentText("Báo cáo: " + selected.getReportName());
        
        if (alert.showAndWait().orElse(javafx.scene.control.ButtonType.CANCEL) == javafx.scene.control.ButtonType.OK) {
            btnDelete.setDisable(true);
            new Thread(() -> {
                try {
                    reportService.deleteReport(selected.getId());
                    Platform.runLater(() -> {
                        UIUtils.showInfo("Thành công", "Đã xóa báo cáo!");
                        loadHistory();
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

    @FXML
    private void handleViewDetail() {
        ReportHistory selected = tableView.getSelectionModel().getSelectedItem();
        if (selected == null) return;
        openReportDetail(selected.getId());
    }

    @FXML
    private void handleGenerateReport() {
        String periodTypeLabel = cbPeriod.getValue();
        String periodValue = txtPeriodValue.getText().trim();
        
        if (periodValue.isEmpty()) {
            UIUtils.showError("Lỗi nhập liệu", "Vui lòng nhập giá trị cho kỳ báo cáo (VD: 08/2026)");
            return;
        }

        String periodType = "month";
        if (periodTypeLabel.equals("Theo tháng")) {
            periodType = "month";
            if (!periodValue.matches("^(0[1-9]|1[0-2])/\\d{4}$")) {
                UIUtils.showError("Lỗi định dạng", "Tháng phải có định dạng MM/yyyy (VD: 08/2026)");
                return;
            }
        } else if (periodTypeLabel.equals("Theo quý")) {
            periodType = "quarter";
            if (!periodValue.matches("^[qQ][1-4]/\\d{4}$")) {
                UIUtils.showError("Lỗi định dạng", "Quý phải có định dạng Qx/yyyy (VD: Q3/2026)");
                return;
            }
        } else if (periodTypeLabel.equals("Theo năm")) {
            periodType = "year";
            if (!periodValue.matches("^\\d{4}$")) {
                UIUtils.showError("Lỗi định dạng", "Năm phải có định dạng yyyy (VD: 2026)");
                return;
            }
        }
        final String finalPeriodType = periodType;

        new Thread(() -> {
            try {
                ReportData data = reportService.generateReport(finalPeriodType, periodValue, true);
                Platform.runLater(() -> {
                    UIUtils.showInfo("Thành công", "Đã tạo báo cáo thành công!");
                    loadHistory();
                    showReportDetailDialog(data);
                });
            } catch (ApiException e) {
                Platform.runLater(() -> UIUtils.showError("Lỗi tạo báo cáo", e.getMessage()));
            }
        }).start();
    }

    private void openReportDetail(int reportId) {
        new Thread(() -> {
            try {
                ReportData data = reportService.getReportById(reportId);
                Platform.runLater(() -> showReportDetailDialog(data));
            } catch (ApiException e) {
                Platform.runLater(() -> UIUtils.showError("Lỗi lấy dữ liệu báo cáo", e.getMessage()));
            }
        }).start();
    }

    private void showReportDetailDialog(ReportData data) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/report_detail.fxml"));
            Parent root = loader.load();
            
            ReportDetailController controller = loader.getController();
            controller.initData(data);

            Stage stage = new Stage();
            stage.setTitle("Chi tiết Báo cáo");
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setScene(new Scene(root, 900, 600));
            stage.show();
        } catch (Exception e) {
            e.printStackTrace();
            UIUtils.showError("Lỗi giao diện", "Không thể mở màn hình chi tiết báo cáo: " + e.getMessage());
        }
    }
}

