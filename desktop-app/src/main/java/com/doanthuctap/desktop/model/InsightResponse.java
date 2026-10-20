package com.doanthuctap.desktop.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class InsightResponse {
    private String question;
    
    @JsonProperty("answer_text")
    private String answerText;
    
    private List<InsightTableItem> table;

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getAnswerText() {
        return answerText;
    }

    public void setAnswerText(String answerText) {
        this.answerText = answerText;
    }

    public List<InsightTableItem> getTable() {
        return table;
    }

    public void setTable(List<InsightTableItem> table) {
        this.table = table;
    }
}
