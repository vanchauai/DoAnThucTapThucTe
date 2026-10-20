package com.doanthuctap.android.config

object AppConfig {
    // Note: 10.0.2.2 is the alias to your host loopback interface (localhost) in Android Emulator.
    // If you run on a real device, change this to your machine's local IP address (e.g. "http://192.168.100.221:8000/api/v1/")
    var BASE_URL = "http://192.168.100.221:8000/api/v1/"
    const val PREF_FILE_NAME = "app_preferences"
    const val TOKEN_KEY = "jwt_token"
}
