package com.example.p_article.ui.article

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.Article
import com.example.p_article.data.ArticleRepository
import com.example.p_article.data.FakeArticleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ArticleViewModel @JvmOverloads constructor(
    savedStateHandle: SavedStateHandle,
    private val repo: ArticleRepository = FakeArticleRepository,
) : ViewModel() {
    private val articleId: Int = checkNotNull(savedStateHandle["articleId"])
    private val _article = MutableStateFlow<Article?>(null)
    val article: StateFlow<Article?> = _article.asStateFlow()

    init { viewModelScope.launch { _article.value = repo.getArticle(articleId) } }
}