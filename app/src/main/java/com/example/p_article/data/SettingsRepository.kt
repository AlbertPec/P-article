package com.example.p_article.data

import android.content.Context
import androidx.core.content.edit
import com.example.p_article.BuildConfig
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class SettingsRepository(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    // null until the user picks a mode, which means follow the system
    private val _darkMode = MutableStateFlow(
        if (prefs.contains(KEY_DARK_MODE)) prefs.getBoolean(KEY_DARK_MODE, false) else null
    )
    val darkMode: StateFlow<Boolean?> = _darkMode.asStateFlow()

    private val _serverUrl = MutableStateFlow(
        prefs.getString(KEY_SERVER_URL, null) ?: BuildConfig.PARSER_SERVER_URL
    )
    val serverUrl: StateFlow<String> = _serverUrl.asStateFlow()

    fun setDarkMode(enabled: Boolean) {
        prefs.edit { putBoolean(KEY_DARK_MODE, enabled) }
        _darkMode.value = enabled
    }

    fun setServerUrl(address: String) {
        val trimmed = address.trim().trimEnd('/')
        if (trimmed.isEmpty()) {
            prefs.edit { remove(KEY_SERVER_URL) }
            _serverUrl.value = BuildConfig.PARSER_SERVER_URL
            return
        }
        val url = if ("://" in trimmed) trimmed else "http://$trimmed"
        prefs.edit { putString(KEY_SERVER_URL, url) }
        _serverUrl.value = url
    }

    private companion object {
        const val KEY_DARK_MODE = "dark_mode"
        const val KEY_SERVER_URL = "server_url"
    }
}
