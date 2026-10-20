package com.doanthuctap.desktop.controller;

import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.XYChart;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class PredictionController {

    @FXML private LineChart<String, Number> revenueChart;
    @FXML private VBox vboxWarnings;

    private static class DailyData {
        String day;
        double revenue;
        DailyData(String day, double revenue) {
            this.day = day;
            this.revenue = revenue;
        }
    }

    @FXML
    public void initialize() {
        // Fetch/Generate 90 days of daily data
        new Thread(() -> {
            try {
                List<DailyData> historicalData = generateMockDailyData(90);
                javafx.application.Platform.runLater(() -> processAndRenderChart(historicalData));
            } catch (Exception e) {
                javafx.application.Platform.runLater(() -> {
                    com.doanthuctap.desktop.util.UIUtils.showError("Lỗi", "Không thể lấy dữ liệu: " + e.getMessage());
                });
            }
        }).start();
    }

    private List<DailyData> generateMockDailyData(int days) {
        List<DailyData> dataList = new ArrayList<>();
        java.io.File file = new java.io.File("D:\\\\DoAn\\\\DoAnThucTapThucTe\\\\orders_3months.csv");
        if (file.exists()) {
            java.util.Map<LocalDate, Double> dailyRevenue = new java.util.TreeMap<>();
            try (java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(new java.io.FileInputStream(file), java.nio.charset.StandardCharsets.UTF_8))) {
                String line = br.readLine(); // skip header
                DateTimeFormatter inFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
                while ((line = br.readLine()) != null) {
                    String[] cols = line.split(",");
                    if (cols.length >= 5) {
                        LocalDate date = LocalDate.parse(cols[1].trim(), inFormatter);
                        int qty = Integer.parseInt(cols[3].trim());
                        double price = Double.parseDouble(cols[4].trim());
                        dailyRevenue.put(date, dailyRevenue.getOrDefault(date, 0.0) + (qty * price));
                    }
                }
                DateTimeFormatter outFormatter = DateTimeFormatter.ofPattern("dd/MM");
                for (java.util.Map.Entry<LocalDate, Double> entry : dailyRevenue.entrySet()) {
                    dataList.add(new DailyData(entry.getKey().format(outFormatter), entry.getValue()));
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return dataList;
    }

    private void processAndRenderChart(List<DailyData> historicalData) {
        if (historicalData.isEmpty()) return;

        // Polynomial degree 4
        int degree = 4;
        double[] coefs = calculatePolynomialRegression(historicalData, degree);

        List<Double> predictions = new ArrayList<>();
        double sse = 0; 
        for (int i = 0; i < historicalData.size(); i++) {
            double x = (i + 1.0) / historicalData.size(); // Scale to 0-1 for stability
            double yPred = 0;
            for (int j = 0; j <= degree; j++) {
                yPred += coefs[j] * Math.pow(x, j);
            }
            predictions.add(yPred);
            double error = historicalData.get(i).revenue - yPred;
            sse += error * error;
        }

        // Standard error of estimate
        double stdDev = Math.sqrt(sse / (historicalData.size() - (degree + 1)));
        double confidenceMultiplier = 2.0; // 2 StdDev for ~95% bounds

        // Detect Outliers
        vboxWarnings.getChildren().clear();
        Label warnTitle = new Label("Cảnh báo bất thường (Outliers):");
        warnTitle.setStyle("-fx-font-weight: bold; -fx-text-fill: #FCA5A5; -fx-font-size: 14px;");
        vboxWarnings.getChildren().add(warnTitle);
        boolean hasOutlier = false;
        
        for (int i = 0; i < historicalData.size(); i++) {
            double actual = historicalData.get(i).revenue;
            double pred = predictions.get(i);
            if (actual < pred - confidenceMultiplier * stdDev || actual > pred + confidenceMultiplier * stdDev) {
                hasOutlier = true;
                String type = actual < pred ? "giảm" : "tăng";
                Label lbl = new Label("• Ngày " + historicalData.get(i).day + ": Doanh thu " + type + " đột biến (" 
                        + String.format("%,.0f", actual) + " VND) so với kỳ vọng.");
                lbl.setStyle("-fx-text-fill: #FCA5A5;");
                vboxWarnings.getChildren().add(lbl);
            }
        }
        
        vboxWarnings.setVisible(hasOutlier);
        vboxWarnings.setManaged(hasOutlier);

        // Populate Chart
        revenueChart.getData().clear();

        XYChart.Series<String, Number> seriesActual = new XYChart.Series<>();
        seriesActual.setName("Thực tế");
        
        XYChart.Series<String, Number> seriesTrend = new XYChart.Series<>();
        seriesTrend.setName("Xu hướng (Bậc 4)");
        
        XYChart.Series<String, Number> seriesUpper = new XYChart.Series<>();
        seriesUpper.setName("Cận trên (+2σ)");
        
        XYChart.Series<String, Number> seriesLower = new XYChart.Series<>();
        seriesLower.setName("Cận dưới (-2σ)");

        for (int i = 0; i < historicalData.size(); i++) {
            String day = historicalData.get(i).day;
            double actual = historicalData.get(i).revenue;
            double pred = Math.max(0, predictions.get(i));
            double upper = pred + confidenceMultiplier * stdDev;
            double lower = Math.max(0, pred - confidenceMultiplier * stdDev);

            seriesActual.getData().add(new XYChart.Data<>(day, actual));
            seriesTrend.getData().add(new XYChart.Data<>(day, pred));
            seriesUpper.getData().add(new XYChart.Data<>(day, upper));
            seriesLower.getData().add(new XYChart.Data<>(day, lower));
        }

        revenueChart.getData().addAll(seriesActual, seriesTrend, seriesUpper, seriesLower);

        // Apply styles after nodes are attached
        javafx.application.Platform.runLater(() -> {
            if (seriesActual.getNode() != null) seriesActual.getNode().setStyle("-fx-stroke: #10B981; -fx-stroke-width: 2px;"); // Green
            if (seriesTrend.getNode() != null) seriesTrend.getNode().setStyle("-fx-stroke: #00A8E8; -fx-stroke-width: 3px;"); // Blue
            if (seriesUpper.getNode() != null) seriesUpper.getNode().setStyle("-fx-stroke: #64748B; -fx-stroke-width: 1px; -fx-stroke-dash-array: 5 5;"); // Gray dashed
            if (seriesLower.getNode() != null) seriesLower.getNode().setStyle("-fx-stroke: #64748B; -fx-stroke-width: 1px; -fx-stroke-dash-array: 5 5;"); // Gray dashed

            // Hide symbols for trend and bounds
            for (XYChart.Data<String, Number> data : seriesTrend.getData()) {
                if (data.getNode() != null) data.getNode().setVisible(false);
            }
            for (XYChart.Data<String, Number> data : seriesUpper.getData()) {
                if (data.getNode() != null) data.getNode().setVisible(false);
            }
            for (XYChart.Data<String, Number> data : seriesLower.getData()) {
                if (data.getNode() != null) data.getNode().setVisible(false);
            }
        });
    }

    private double[] calculatePolynomialRegression(List<DailyData> dataList, int degree) {
        int n = dataList.size();
        int matrixSize = degree + 1;
        double[][] X = new double[matrixSize][matrixSize];
        double[] Y = new double[matrixSize];

        for (int i = 0; i < matrixSize; i++) {
            for (int j = 0; j < matrixSize; j++) {
                double sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += Math.pow((k + 1.0) / n, i + j);
                }
                X[i][j] = sum;
            }
            double sumY = 0;
            for (int k = 0; k < n; k++) {
                sumY += dataList.get(k).revenue * Math.pow((k + 1.0) / n, i);
            }
            Y[i] = sumY;
        }

        return solveGaussianElimination(X, Y);
    }

    private double[] solveGaussianElimination(double[][] A, double[] B) {
        int n = B.length;
        for (int p = 0; p < n; p++) {
            int max = p;
            for (int i = p + 1; i < n; i++) {
                if (Math.abs(A[i][p]) > Math.abs(A[max][p])) {
                    max = i;
                }
            }
            double[] temp = A[p]; A[p] = A[max]; A[max] = temp;
            double t = B[p]; B[p] = B[max]; B[max] = t;

            if (Math.abs(A[p][p]) < 1e-10) continue; // Avoid division by zero

            for (int i = p + 1; i < n; i++) {
                double alpha = A[i][p] / A[p][p];
                B[i] -= alpha * B[p];
                for (int j = p; j < n; j++) {
                    A[i][j] -= alpha * A[p][j];
                }
            }
        }
        
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {
            double sum = 0.0;
            for (int j = i + 1; j < n; j++) {
                sum += A[i][j] * x[j];
            }
            if (Math.abs(A[i][i]) > 1e-10) {
                x[i] = (B[i] - sum) / A[i][i];
            }
        }
        return x;
    }
}



