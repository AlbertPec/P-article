package com.example.p_article.ui.feed

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.PArticleApplication
import com.example.p_article.R
import com.example.p_article.data.Panel
import com.example.p_article.data.repository.ParticleRepository
import com.example.p_article.domain.feed.FeedBuilder
import com.example.p_article.domain.feed.FeedCard
import com.example.p_article.domain.feed.FeedContext
import com.example.p_article.domain.feed.FeedParticle
import com.example.p_article.domain.feed.ParticleKey
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import kotlin.random.Random

class FeedViewModel(application: Application) : AndroidViewModel(application) {
    private val container = (application as PArticleApplication).container
    private val repo: ParticleRepository = container.particleRepository
    private val builder: FeedBuilder = container.feedBuilder

    val serverUrl: StateFlow<String> = container.settings.serverUrl

    private val source = repo.allPanels()

    private var sessionSeed = Random.nextLong()
    private val snapshot = MutableStateFlow<List<FeedCard>?>(null)   // frozen order

    // Content is live, order is frozen: the snapshot is only filtered, never re-sorted.
    val panels: StateFlow<List<Panel>> = combine(source, snapshot) { all, cards ->
        if (cards == null) return@combine emptyList()
        val current = builder.currentKeys(all.toFeedParticles())
        val byId = all.associateBy { it.imagePath }
        cards.filter { it.particle in current }.mapNotNull { byId[it.panelId] }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    private var syncedUrl: String? = null

    init {
        viewModelScope.launch {
            source.collect { all ->
                val current = builder.currentKeys(all.toFeedParticles())
                val shown = snapshot.value?.map { it.particle }?.toSet().orEmpty()
                if (shown.isEmpty() || !current.containsAll(shown)) snapshot.value = build(all)
            }
        }
    }

    private fun build(all: List<Panel>): List<FeedCard> =
        builder.build(all.toFeedParticles(), FeedContext(sessionSeed))

    /** Pull-to-refresh: new order and new panel mix. */
    fun refresh() {
        viewModelScope.launch {
            sessionSeed = Random.nextLong()
            snapshot.value = build(source.first())
        }
    }

    /** Call on ON_RESUME. Re-ranks only if the set of current particles changed. */
    fun onResume() {
        viewModelScope.launch {
            val all = source.first()
            val shown = snapshot.value?.map { it.particle }?.toSet().orEmpty()
            if (builder.currentKeys(all.toFeedParticles()) != shown) snapshot.value = build(all)
        }
    }

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

private fun List<Panel>.toFeedParticles(): List<FeedParticle> =
    groupBy { ParticleKey(it.articleId, it.partNo) }
        .map { (key, group) -> FeedParticle(key, group.first().status, group.map { it.imagePath }) }