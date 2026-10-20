package com.doanthuctap.android.network

import com.doanthuctap.android.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.*

interface ApiService {
    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): TokenResponse

    @GET("users/me")
    suspend fun getCurrentUser(): User

    @GET("data-sources")
    suspend fun getDataSources(): ListResponse<DataSource>

    @POST("data-sources/{id}/sync")
    suspend fun syncDataSource(@Path("id") id: Int): SyncResponse

    @GET("reports/history")
    suspend fun getReportHistory(): ListResponse<ReportHistory>

    @GET("reports/{id}")
    suspend fun getReportData(@Path("id") id: Int): ReportData

    @POST("reports/generate")
    suspend fun generateReport(@Body body: Map<String, @JvmSuppressWildcards Any>): ReportData

    @Multipart
    @POST("prediction/predict-sales")
    suspend fun predictSales(
        @Part file: MultipartBody.Part,
        @Part("branch_id") branchId: RequestBody?
    ): ReportData

    @POST("assistant/ask")
    suspend fun askAssistant(@Body body: Map<String, String>): InsightResponse
}
