package com.example.p_article.ui.feed

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.PArticleApplication
import com.example.p_article.R
import com.example.p_article.data.Panel
import com.example.p_article.data.repository.ParticleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class FeedViewModel(application: Application) : AndroidViewModel(application) {
    private val container = (application as PArticleApplication).container
    private val repo: ParticleRepository = container.particleRepository

    val serverUrl: StateFlow<String> = container.settings.serverUrl

    val panels: StateFlow<List<Panel>> = repo.feed()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    private var syncedUrl: String? = null

    fun needsSync(): Boolean = syncedUrl != serverUrl.value

    fun sync() {
        if (!needsSync()) return
        syncedUrl = serverUrl.value
        viewModelScope.launch {
            repo.sync().onFailure {
                _message.value = getApplication<Application>().getString(R.string.error_sync_failed)
            }
        }
    }

    fun onLocalNetworkPermissionDenied() {
        syncedUrl = serverUrl.value
        _message.value = getApplication<Application>().getString(R.string.local_network_permission_sync)
    }

    fun messageShown() {
        _message.value = null
    }
}
