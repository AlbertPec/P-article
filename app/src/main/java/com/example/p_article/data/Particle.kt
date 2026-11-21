package com.example.p_article.data

data class Particle(
    val articleId: String,          // link to the parent
    val partNo: Int,                // 1-based, as on the server
    val articleTitle: String,
    val content: String,            // Markdown
    val status: ReadingStatus = ReadingStatus.New,
)
