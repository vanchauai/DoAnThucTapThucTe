package com.doanthuctap.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PredictionScreen() {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Prediction Models", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Upload your data file to predict future sales trends.")
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = { /* TODO: File Picker */ }) {
            Text("Select File (.csv, .xlsx)")
        }
        // ... file selection and calling viewModel.predictSales
    }
}
