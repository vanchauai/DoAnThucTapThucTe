package com.doanthuctap.android.session

import android.content.Context
import android.content.SharedPreferences
import com.doanthuctap.android.config.AppConfig
import com.doanthuctap.android.model.User
import com.doanthuctap.android.network.ApiClient

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences(AppConfig.PREF_FILE_NAME, Context.MODE_PRIVATE)

    var currentUser: User? = null

    init {
        // Load token from prefs to ApiClient
        val savedToken = prefs.getString(AppConfig.TOKEN_KEY, null)
        ApiClient.setToken(savedToken)
    }

    fun saveToken(token: String) {
        prefs.edit().putString(AppConfig.TOKEN_KEY, token).apply()
        ApiClient.setToken(token)
    }

    fun getToken(): String? {
        return prefs.getString(AppConfig.TOKEN_KEY, null)
    }

    fun clearSession() {
        prefs.edit().remove(AppConfig.TOKEN_KEY).apply()
        ApiClient.setToken(null)
        currentUser = null
    }

    companion object {
        @Volatile
        private var instance: SessionManager? = null

        fun getInstance(context: Context): SessionManager {
            return instance ?: synchronized(this) {
                instance ?: SessionManager(context.applicationContext).also { instance = it }
            }
        }
    }
}
