package com.example.p_article.ui.article

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.viewModelScope
import com.example.p_article.PArticleApplication
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import com.example.p_article.data.repository.ParticleRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ArticleViewModel(
    application: Application,
    savedStateHandle: SavedStateHandle,
) : AndroidViewModel(application) {
    private val repo: ParticleRepository = (application as PArticleApplication).container.particleRepository
    private val articleId: String = checkNotNull(savedStateHandle["articleId"]) { "articleId is required" }
    private val partNo: Int = checkNotNull(savedStateHandle["partNo"]) { "partNo is required" }

    val particle: StateFlow<Particle?> = repo.particle(articleId, partNo)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    fun mark(decision: ReadingStatus) {
        viewModelScope.launch {
            repo.setStatus(articleId, partNo, decision)
        }
    }
}
