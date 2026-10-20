package com.doanthuctap.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.doanthuctap.android.viewmodel.MainViewModel

@Composable
fun DashboardScreen(viewModel: MainViewModel) {
    val user by viewModel.user.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        if (user != null) {
            Text(
                text = "Welcome, ${user?.fullName}",
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                text = "Role: ${user?.role} - Branch: ${user?.branchId ?: "All"}",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(24.dp))
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Select 'Sources' below to manage data.", style = MaterialTheme.typography.bodyLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Select 'Reports' to view generated reports.", style = MaterialTheme.typography.bodyLarge)
                }
            }
        } else {
            CircularProgressIndicator()
        }
    }
}
