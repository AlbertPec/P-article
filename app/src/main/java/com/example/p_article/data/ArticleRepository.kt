package com.example.p_article.data

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

interface ArticleRepository {
    val decisions: StateFlow<Map<String, ReadingStatus>>
    suspend fun getArticles(): List<Article>
    suspend fun getArticle(id: String): Article?
    fun markArticle(id: String, decision: ReadingStatus)
}

object FakeArticleRepository : ArticleRepository {
    private val articles = List(20) { i ->
        Article(
            id = "uuid-$i",
            title = "Article title #$i",
            authors = listOf("Author $i"),
            affiliations = listOf("University $i"),
            topic = "Topic $i",
            particleCount = 3,
        )
    }
    override suspend fun getArticles() = articles
    override suspend fun getArticle(id: String) = articles.find { it.id == id }
    private val _decisions = MutableStateFlow<Map<String, ReadingStatus>>(emptyMap())
    override val decisions = _decisions.asStateFlow()
    override fun markArticle(id: String, decision: ReadingStatus) {
        _decisions.update { it + (id to decision) }
    }
}
