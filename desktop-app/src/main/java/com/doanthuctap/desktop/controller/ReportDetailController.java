package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.ReportData;
import com.doanthuctap.desktop.session.UserSession;
import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.chart.BarChart;
import javafx.scene.chart.XYChart;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

public class ReportDetailController {

    @FXML private Label lblTotalRevenue;
    @FXML private Label lblRevenueChange;
    @FXML private Label lblTotalOrders;
    @FXML private Label lblAvgRevenue;

    @FXML private BarChart<String, Number> revenueChart;

    @FXML private TableView<ReportData.TopProduct> tblTopProducts;
    @FXML private TableColumn<ReportData.TopProduct, String> colProductName;
    @FXML private TableColumn<ReportData.TopProduct, Integer> colProductQuantity;

    @FXML
    public void initialize() {
        colProductName.setCellValueFactory(new PropertyValueFactory<>("productName"));
        colProductQuantity.setCellValueFactory(new PropertyValueFactory<>("totalQuantity"));
    }

    public void initData(ReportData data) {
        if (data == null) return;

        // 1. Gán số liệu tổng quan
        if (data.getSummary() != null) {
            lblTotalRevenue.setText(String.format("%,.0f đ", data.getSummary().getTotalRevenue()));
            lblTotalOrders.setText(String.valueOf(data.getSummary().getTotalOrders()));
            lblAvgRevenue.setText(String.format("%,.0f đ", data.getSummary().getAvgRevenuePerOrder()));
            
            double change = data.getSummary().getRevenueChangePercent();
            if (change > 0) {
                lblRevenueChange.setText(String.format("+%.2f%%", change));
                lblRevenueChange.setStyle("-fx-text-fill: #4CAF50; -fx-font-weight: bold; -fx-font-size: 24px;");
            } else if (change < 0) {
                lblRevenueChange.setText(String.format("%.2f%%", change));
                lblRevenueChange.setStyle("-fx-text-fill: #F44336; -fx-font-weight: bold; -fx-font-size: 24px;");
            } else {
                lblRevenueChange.setText("0%");
            }
        }

        // 2. Vẽ biểu đồ
        if (data.getChartData() != null) {
            XYChart.Series<String, Number> series = new XYChart.Series<>();
            for (ReportData.ChartData cd : data.getChartData()) {
                series.getData().add(new XYChart.Data<>(cd.getLabel(), cd.getRevenue()));
            }
            revenueChart.getData().clear();
            revenueChart.getData().add(series);
        }

        // 3. Load bảng Top Products
        if (data.getTopProducts() != null) {
            tblTopProducts.setItems(FXCollections.observableArrayList(data.getTopProducts()));
        }
    }

    @FXML
    private void handleClose() {
        Stage stage = (Stage) lblTotalRevenue.getScene().getWindow();
        stage.close();
    }
}


