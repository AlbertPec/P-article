package com.example.p_article.data.remote.dto

data class ArticleSummaryDto(
    val id: String,
    val particleCount: Int,
)

data class ArticleDto(
    val id: String,
    val title: String,
    val authors: List<String>,
    val affiliations: List<String>,
    val topic: String,
    val particleCount: Int,
)
