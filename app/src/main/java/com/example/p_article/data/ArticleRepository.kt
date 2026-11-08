package com.example.p_article.data

interface ArticleRepository {
    suspend fun getArticles(): List<Article>
    suspend fun getArticle(id: Int): Article?
}

object FakeArticleRepository : ArticleRepository {
    private val articles = List(20) { i ->
        Article(
            id = i,
            title = "Article title #$i",
            imageUrl = "https://picsum.photos/seed/$i/600/400",
            content = "Lorem ipsum dolor sit amet... ".repeat(30),
        )
    }
    override suspend fun getArticles() = articles
    override suspend fun getArticle(id: Int) = articles.find { it.id == id }
}