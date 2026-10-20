package com.doanthuctap.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.doanthuctap.android.repository.AppRepository
import com.doanthuctap.android.session.SessionManager
import com.doanthuctap.android.ui.screens.LoginScreen
import com.doanthuctap.android.ui.screens.MainScreen
import com.doanthuctap.android.ui.theme.DoAnThucTeAndroidTheme
import com.doanthuctap.android.viewmodel.AuthViewModel
import com.doanthuctap.android.viewmodel.AuthViewModelFactory
import com.doanthuctap.android.viewmodel.MainViewModel
import com.doanthuctap.android.viewmodel.MainViewModelFactory

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        val sessionManager = SessionManager.getInstance(this)
        val repository = AppRepository(sessionManager)
        
        setContent {
            DoAnThucTeAndroidTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppNavigation(repository, sessionManager)
                }
            }
        }
    }
}

@Composable
fun AppNavigation(repository: AppRepository, sessionManager: SessionManager) {
    var isLoggedIn by remember { mutableStateOf(sessionManager.getToken() != null) }

    if (!isLoggedIn) {
        val authViewModel: AuthViewModel = viewModel(factory = AuthViewModelFactory(repository))
        LoginScreen(
            viewModel = authViewModel,
            onLoginSuccess = { isLoggedIn = true }
        )
    } else {
        val mainViewModel: MainViewModel = viewModel(factory = MainViewModelFactory(repository))
        // Load user initially if not loaded
        if (sessionManager.currentUser != null) {
            mainViewModel.setUser(sessionManager.currentUser)
        }
        
        MainScreen(
            viewModel = mainViewModel,
            onLogout = {
                sessionManager.clearSession()
                isLoggedIn = false
            }
        )
    }
}