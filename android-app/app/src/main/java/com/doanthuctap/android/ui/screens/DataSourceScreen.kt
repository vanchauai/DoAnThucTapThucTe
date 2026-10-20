package com.doanthuctap.android.ui.screens

import android.widget.Toast
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.doanthuctap.android.model.DataSource
import com.doanthuctap.android.viewmodel.MainViewModel
import com.doanthuctap.android.viewmodel.UiState

@Composable
fun DataSourceScreen(viewModel: MainViewModel) {
    val state by viewModel.dataSources.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        viewModel.loadDataSources()
    }

    Column(modifier = Modifier.fillMaxSize()) {
        when (val uiState = state) {
            is UiState.Loading -> {
                CircularProgressIndicator(modifier = Modifier.padding(16.dp))
            }
            is UiState.Success -> {
                LazyColumn {
                    items(uiState.data) { source ->
                        DataSourceItem(source) {
                            viewModel.syncDataSource(source.id) { success, msg ->
                                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                                if (success) viewModel.loadDataSources()
                            }
                        }
                    }
                }
            }
            is UiState.Error -> {
                Text("Error: ${uiState.message}", color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun DataSourceItem(source: DataSource, onSyncClick: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(source.name, style = MaterialTheme.typography.titleLarge)
            Text("Type: ${source.type}")
            Text("Status: ${source.status ?: "N/A"}")
            Text("Last Synced: ${source.lastSyncedAt ?: "Never"}")
            Spacer(modifier = Modifier.height(8.dp))
            Button(onClick = onSyncClick) {
                Text("Sync Now")
            }
        }
    }
}
