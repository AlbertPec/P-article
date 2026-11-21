package com.example.p_article.ui.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.example.p_article.PArticleApplication
import kotlinx.coroutines.flow.StateFlow

class SettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PArticleApplication).container.settings

    val darkMode: StateFlow<Boolean?> = repo.darkMode
    val serverUrl: StateFlow<String> = repo.serverUrl

    fun setDarkMode(enabled: Boolean) = repo.setDarkMode(enabled)

    fun setServerUrl(address: String) = repo.setServerUrl(address)
}
