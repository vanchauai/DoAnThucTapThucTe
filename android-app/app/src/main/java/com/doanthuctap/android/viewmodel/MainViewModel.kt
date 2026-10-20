package com.doanthuctap.android.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.doanthuctap.android.model.*
import com.doanthuctap.android.repository.AppRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

class MainViewModel(private val repository: AppRepository) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user

    private val _dataSources = MutableStateFlow<UiState<List<DataSource>>>(UiState.Loading)
    val dataSources: StateFlow<UiState<List<DataSource>>> = _dataSources

    private val _reportHistory = MutableStateFlow<UiState<List<ReportHistory>>>(UiState.Loading)
    val reportHistory: StateFlow<UiState<List<ReportHistory>>> = _reportHistory

    private val _reportData = MutableStateFlow<UiState<ReportData?>>(UiState.Success(null))
    val reportData: StateFlow<UiState<ReportData?>> = _reportData

    private val _insightResponse = MutableStateFlow<UiState<InsightResponse?>>(UiState.Success(null))
    val insightResponse: StateFlow<UiState<InsightResponse?>> = _insightResponse

    fun setUser(user: User?) {
        _user.value = user
    }

    fun loadDataSources() {
        viewModelScope.launch {
            _dataSources.value = UiState.Loading
            repository.getDataSources().fold(
                onSuccess = { _dataSources.value = UiState.Success(it) },
                onFailure = { _dataSources.value = UiState.Error(it.message ?: "Unknown error") }
            )
        }
    }

    fun syncDataSource(id: Int, onResult: (Boolean, String) -> Unit) {
        viewModelScope.launch {
            repository.syncDataSource(id).fold(
                onSuccess = { onResult(true, it.message) },
                onFailure = { onResult(false, it.message ?: "Sync failed") }
            )
        }
    }

    fun loadReportHistory() {
        viewModelScope.launch {
            _reportHistory.value = UiState.Loading
            repository.getReportHistory().fold(
                onSuccess = { _reportHistory.value = UiState.Success(it) },
                onFailure = { _reportHistory.value = UiState.Error(it.message ?: "Unknown error") }
            )
        }
    }

    fun generateReport(branchId: String?) {
        viewModelScope.launch {
            _reportData.value = UiState.Loading
            repository.generateReport(branchId).fold(
                onSuccess = { _reportData.value = UiState.Success(it) },
                onFailure = { _reportData.value = UiState.Error(it.message ?: "Unknown error") }
            )
        }
    }

    fun askAssistant(question: String) {
        viewModelScope.launch {
            _insightResponse.value = UiState.Loading
            repository.askAssistant(question).fold(
                onSuccess = { _insightResponse.value = UiState.Success(it) },
                onFailure = { _insightResponse.value = UiState.Error(it.message ?: "Unknown error") }
            )
        }
    }

    fun predictSales(file: File, branchId: String?, onResult: (UiState<ReportData>) -> Unit) {
        viewModelScope.launch {
            onResult(UiState.Loading)
            repository.predictSales(file, branchId).fold(
                onSuccess = { onResult(UiState.Success(it)) },
                onFailure = { onResult(UiState.Error(it.message ?: "Unknown error")) }
            )
        }
    }
}

class MainViewModelFactory(private val repository: AppRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
