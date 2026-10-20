package com.doanthuctap.desktop.controller;

import com.doanthuctap.desktop.model.InsightResponse;
import com.doanthuctap.desktop.model.InsightTableItem;
import com.doanthuctap.desktop.model.User;
import com.doanthuctap.desktop.network.ApiException;
import com.doanthuctap.desktop.service.AuthService;
import com.doanthuctap.desktop.service.InsightService;
import com.doanthuctap.desktop.util.UIUtils;
import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;

import java.util.LinkedHashMap;
import java.util.Map;

public class DataAssistantController {

    @FXML private VBox questionsContainer;
    @FXML private Label lblQuestion;
    @FXML private HBox loadingBox;
    @FXML private VBox answerBox;
    @FXML private Label lblAnswerText;
    @FXML private TableView<InsightTableItem> dataTable;
    @FXML private TableColumn<InsightTableItem, String> colLabel;
    @FXML private TableColumn<InsightTableItem, String> colValue;

    private InsightService insightService;
    private User currentUser;

    @FXML
    public void initialize() {
        insightService = new InsightService();
        currentUser = com.doanthuctap.desktop.session.UserSession.getInstance().getUser();

        setupTable();
        loadQuestions();
    }

    private void setupTable() {
        colLabel.setCellValueFactory(cellData -> new SimpleStringProperty(cellData.getValue().getLabel()));
        colValue.setCellValueFactory(cellData -> new SimpleStringProperty(cellData.getValue().getValue()));
    }

    private void loadQuestions() {
        questionsContainer.getChildren().clear();
        
        Map<String, String> qMap = new LinkedHashMap<>();
        qMap.put("revenue_this_month", "1. Doanh thu tháng này so với tháng trước thế nào?");
        qMap.put("top_product", "2. Sản phẩm nào bán chạy nhất tháng này?");
        
        qMap.put("forecast", "4. Xu hướng doanh thu sắp tới dự báo thế nào?");
        qMap.put("data_source_errors", "5. Có nguồn dữ liệu nào đang gặp lỗi không?");
        qMap.put("anomaly_alert", "6. Có phát hiện dữ liệu bất thường nào gần đây không?");

        for (Map.Entry<String, String> entry : qMap.entrySet()) {
            Button btn = new Button(entry.getValue());
            btn.getStyleClass().add("btn-question");
            btn.setStyle("-fx-background-color: transparent; -fx-text-fill: #94A3B8; -fx-alignment: CENTER_LEFT; -fx-padding: 10 5; -fx-cursor: hand;");
            btn.setMaxWidth(Double.MAX_VALUE);
            btn.setWrapText(true);
            
            btn.setOnMouseEntered(e -> btn.setStyle("-fx-background-color: #1E2D40; -fx-text-fill: white; -fx-background-radius: 8; -fx-alignment: CENTER_LEFT; -fx-padding: 10 5; -fx-cursor: hand;"));
            btn.setOnMouseExited(e -> btn.setStyle("-fx-background-color: transparent; -fx-text-fill: #94A3B8; -fx-alignment: CENTER_LEFT; -fx-padding: 10 5; -fx-cursor: hand;"));
            
            btn.setOnAction(e -> askQuestion(entry.getKey(), entry.getValue()));
            questionsContainer.getChildren().add(btn);
        }
    }

    private void askQuestion(String questionId, String questionText) {
        lblQuestion.setText(questionText);
        answerBox.setVisible(false);
        loadingBox.setVisible(true);
        loadingBox.setManaged(true);

        new Thread(() -> {
            try {
                InsightResponse response = insightService.getAnswer(questionId);
                
                Platform.runLater(() -> {
                    lblAnswerText.setText(response.getAnswerText());
                    
                    if (response.getTable() != null && !response.getTable().isEmpty()) {
                        dataTable.getItems().clear();
                        dataTable.getItems().addAll(response.getTable());
                        dataTable.setVisible(true);
                        dataTable.setManaged(true);
                    } else {
                        dataTable.setVisible(false);
                        dataTable.setManaged(false);
                    }
                    
                    loadingBox.setVisible(false);
                    loadingBox.setManaged(false);
                    answerBox.setVisible(true);
                });
            } catch (ApiException e) {
                Platform.runLater(() -> {
                    loadingBox.setVisible(false);
                    loadingBox.setManaged(false);
                    UIUtils.showError("Lỗi", e.getMessage());
                });
            }
        }).start();
    }
}


