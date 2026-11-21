package com.example.p_article.ui.article

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import com.example.p_article.data.repository.FakeParticleRepository
import com.example.p_article.data.repository.ParticleRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ArticleViewModel @JvmOverloads constructor(
    savedStateHandle: SavedStateHandle,
    private val repo: ParticleRepository = FakeParticleRepository(),
) : ViewModel() {
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
