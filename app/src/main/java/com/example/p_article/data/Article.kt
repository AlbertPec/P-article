package com.example.p_article.data

data class Article(
    val id: String,                 // UUID
    val title: String,
    val authors: List<String>,
    val affiliations: List<String>,
    val topic: String,
    val particleCount: Int,
)
