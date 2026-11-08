package com.example.p_article.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.Article
import com.example.p_article.data.ArticleRepository
import com.example.p_article.data.FakeArticleRepository
import com.example.p_article.data.ReadingStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class FeedViewModel @JvmOverloads constructor(
    private val repo: ArticleRepository = FakeArticleRepository,
) : ViewModel() {
    private val all = MutableStateFlow<List<Article>>(emptyList())

    val articles: StateFlow<List<Article>> =
        combine(all, repo.decisions) { list, decisions ->
            list.filter { decisions[it.id] != ReadingStatus.Hidden }
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init { viewModelScope.launch { all.value = repo.getArticles() } }
}
