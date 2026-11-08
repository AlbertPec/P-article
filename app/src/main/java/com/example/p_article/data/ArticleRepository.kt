package com.example.p_article.data

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

interface ArticleRepository {
    val decisions: StateFlow<Map<Int, ReadingStatus>>
    suspend fun getArticles(): List<Article>
    suspend fun getArticle(id: Int): Article?
    fun markArticle(id: Int, decision: ReadingStatus)
}

object FakeArticleRepository : ArticleRepository {
    private val articles = List(20) { i ->
        Article(
            id = i,
            title = "Article title #$i",
            imageUrl = "https://picsum.photos/seed/$i/600/400",
            content = "Lorem ipsum dolor sit amet... ".repeat(60),
        )
    }
    override suspend fun getArticles() = articles
    override suspend fun getArticle(id: Int) = articles.find { it.id == id }
    private val _decisions = MutableStateFlow<Map<Int, ReadingStatus>>(emptyMap())
    override val decisions = _decisions.asStateFlow()
    override fun markArticle(id: Int, decision: ReadingStatus) {
        _decisions.update { it + (id to decision) }
    }
}