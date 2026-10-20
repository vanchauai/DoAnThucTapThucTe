package com.doanthuctap.android.repository

import com.doanthuctap.android.model.*
import com.doanthuctap.android.network.ApiClient
import com.doanthuctap.android.network.ApiService
import com.doanthuctap.android.session.SessionManager
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class AppRepository(private val sessionManager: SessionManager) {
    private val apiService = ApiClient.createService<ApiService>()

    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val tokenResponse = apiService.login(email, password)
            sessionManager.saveToken(tokenResponse.accessToken)
            
            // fetch user
            val user = apiService.getCurrentUser()
            sessionManager.currentUser = user
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        sessionManager.clearSession()
    }

    suspend fun getDataSources(): Result<List<DataSource>> {
        return try {
            val response = apiService.getDataSources()
            Result.success(response.data)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun syncDataSource(id: Int): Result<SyncResponse> {
        return try {
            val res = apiService.syncDataSource(id)
            Result.success(res)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getReportHistory(): Result<List<ReportHistory>> {
        return try {
            val response = apiService.getReportHistory()
            Result.success(response.data)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun generateReport(branchId: String?): Result<ReportData> {
        return try {
            val params = mutableMapOf<String, Any>("report_type" to "sales")
            if (branchId != null && branchId.isNotEmpty()) {
                params["branch_id"] = branchId
            }
            val data = apiService.generateReport(params)
            Result.success(data)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun askAssistant(question: String): Result<InsightResponse> {
        return try {
            val map = mapOf("question" to question)
            val res = apiService.askAssistant(map)
            Result.success(res)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun predictSales(file: File, branchId: String?): Result<ReportData> {
        return try {
            val requestFile = file.asRequestBody("application/vnd.ms-excel".toMediaTypeOrNull())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)
            val branchPart = branchId?.toRequestBody("text/plain".toMediaTypeOrNull())
            
            val data = apiService.predictSales(filePart, branchPart)
            Result.success(data)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
