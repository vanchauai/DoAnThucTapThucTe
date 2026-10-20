package com.doanthuctap.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.doanthuctap.android.viewmodel.MainViewModel
import com.doanthuctap.android.viewmodel.UiState

@Composable
fun AssistantScreen(viewModel: MainViewModel) {
    var query by remember { mutableStateOf("") }
    val state by viewModel.insightResponse.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        OutlinedTextField(
            value = query,
            onValueChange = { query = it },
            label = { Text("Ask about your data") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { viewModel.askAssistant(query) },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Ask")
        }

        Spacer(modifier = Modifier.height(16.dp))

        when (val uiState = state) {
            is UiState.Loading -> CircularProgressIndicator()
            is UiState.Success -> {
                uiState.data?.let { response ->
                    Card(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Answer:", style = MaterialTheme.typography.titleMedium)
                            Text(response.answerText ?: "No answer")
                            
                            response.table?.let { table ->
                                Spacer(modifier = Modifier.height(8.dp))
                                Text("Data:", style = MaterialTheme.typography.titleSmall)
                                LazyColumn(modifier = Modifier.height(200.dp)) {
                                    items(table) { row ->
                                        Text(row.toString(), style = MaterialTheme.typography.bodySmall)
                                        Divider()
                                    }
                                }
                            }
                        }
                    }
                }
            }
            is UiState.Error -> {
                Text("Error: ${uiState.message}", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}
