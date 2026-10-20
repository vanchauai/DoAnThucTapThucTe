package com.doanthuctap.desktop;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;

/**
 * App: Lớp chính khởi chạy ứng dụng JavaFX.
 * Load giao diện đăng nhập đầu tiên.
 */
public class App extends Application {

    private static Stage primaryStage;

    @Override
    public void start(Stage stage) throws IOException {
        primaryStage = stage;
        setRoot("login", "Đăng nhập hệ thống", 850, 500);
    }

    public static void setRoot(String fxml, String title, int width, int height) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource("/fxml/" + fxml + ".fxml"));
        Parent root = fxmlLoader.load();
        Scene scene = new Scene(root, width, height);
        
        // Nạp file CSS chung
        scene.getStylesheets().add(App.class.getResource("/css/style.css").toExternalForm());
        
        primaryStage.setTitle(title);
        primaryStage.setScene(scene);
        primaryStage.centerOnScreen();
        primaryStage.show();
    }
    
    public static void setRoot(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource("/fxml/" + fxml + ".fxml"));
        Parent root = fxmlLoader.load();
        Scene scene = primaryStage.getScene();
        if (scene == null) {
            scene = new Scene(root);
            primaryStage.setScene(scene);
        } else {
            scene.setRoot(root);
        }
        
        // Bổ sung stylesheet nếu chưa có
        if (scene.getStylesheets().isEmpty()) {
            scene.getStylesheets().add(App.class.getResource("/css/style.css").toExternalForm());
        }
    }

    public static void main(String[] args) {
        launch();
    }
}
