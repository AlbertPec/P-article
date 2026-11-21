package com.example.p_article.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.Panel
import com.example.p_article.data.repository.FakeParticleRepository
import com.example.p_article.data.repository.ParticleRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn

class FeedViewModel @JvmOverloads constructor(
    private val repo: ParticleRepository = FakeParticleRepository(),
) : ViewModel() {
    val panels: StateFlow<List<Panel>> = repo.feed()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
