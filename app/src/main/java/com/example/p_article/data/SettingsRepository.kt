package com.example.p_article.data

import android.content.Context
import androidx.core.content.edit
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

    fun setDarkMode(enabled: Boolean) {
        prefs.edit { putBoolean(KEY_DARK_MODE, enabled) }
        _darkMode.value = enabled
    }

    private companion object {
        const val KEY_DARK_MODE = "dark_mode"
    }
}
