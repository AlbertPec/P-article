package com.example.p_article.ui.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.example.p_article.data.SettingsRepository
import kotlinx.coroutines.flow.StateFlow

class SettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = SettingsRepository(application)

    val darkMode: StateFlow<Boolean?> = repo.darkMode

    fun setDarkMode(enabled: Boolean) = repo.setDarkMode(enabled)
}
