package com.example.p_article.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.Article
import com.example.p_article.data.ArticleRepository
import com.example.p_article.data.FakeArticleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class FeedViewModel @JvmOverloads constructor(
    private val repo: ArticleRepository = FakeArticleRepository,
) : ViewModel() {
    private val _articles = MutableStateFlow<List<Article>>(emptyList())
    val articles: StateFlow<List<Article>> = _articles.asStateFlow()

    init { viewModelScope.launch { _articles.value = repo.getArticles() } }
}