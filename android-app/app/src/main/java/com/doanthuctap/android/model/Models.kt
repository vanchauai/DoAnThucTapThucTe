package com.doanthuctap.android.model

import com.google.gson.annotations.SerializedName

data class User(
    val id: Int,
    @SerializedName("full_name") val fullName: String,
    val email: String,
    val role: String,
    @SerializedName("branch_id") val branchId: String?,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("is_active") val isActive: Boolean
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String
)

data class DataSource(
    val id: Int,
    val name: String,
    @SerializedName("source_type") val type: String,
    val config: Map<String, Any>?,
    @SerializedName("column_mapping") val columnMapping: Map<String, String>?,
    @SerializedName("branch_id") val branchId: String?,
    @SerializedName("created_at") val createdAt: String?,
    val status: String?,
    @SerializedName("last_synced_at") val lastSyncedAt: String?
)

data class ReportHistory(
    val id: Int,
    @SerializedName("report_name") val reportName: String,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("generated_by") val generatedBy: String?,
    val parameters: String?
)

data class ReportData(
    val summary: Summary?,
    @SerializedName("chart_data") val chartData: List<ChartData>?,
    @SerializedName("top_products") val topProducts: List<TopProduct>?,
    @SerializedName("branch_breakdown") val branchBreakdown: List<BranchBreakdown>?
) {
    data class Summary(
        @SerializedName("total_revenue") val totalRevenue: Double,
        @SerializedName("total_orders") val totalOrders: Int,
        @SerializedName("avg_revenue_per_order") val avgRevenuePerOrder: Double,
        @SerializedName("revenue_change_percent") val revenueChangePercent: Double
    )

    data class ChartData(
        val label: String,
        val revenue: Double,
        @SerializedName("forecast_revenue") val forecastRevenue: Double?
    )

    data class TopProduct(
        @SerializedName("product_name") val productName: String,
        @SerializedName("total_quantity") val totalQuantity: Int,
        @SerializedName("total_revenue") val totalRevenue: Double
    )

    data class BranchBreakdown(
        @SerializedName("branch_id") val branchId: String?,
        @SerializedName("branch_name") val branchName: String?,
        @SerializedName("total_revenue") val totalRevenue: Double
    )
}

data class InsightResponse(
    val question: String?,
    @SerializedName("answer_text") val answerText: String?,
    val table: List<Map<String, Any>>?
)

data class SyncResponse(
    val message: String,
    @SerializedName("sync_status") val syncStatus: String?
)

data class OutlierWarning(
    val id: Int,
    @SerializedName("data_point") val dataPoint: String?,
    @SerializedName("warning_level") val warningLevel: String?,
    val message: String?
)

data class ListResponse<T>(
    val data: List<T>,
    val total: Int
)
