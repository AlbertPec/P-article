package com.example.p_article.data

data class Panel(
    val articleId: String,
    val partNo: Int,
    val articleTitle: String,
    val header: String,
    val imagePath: String,          // local file
    val status: ReadingStatus = ReadingStatus.New,
    val position: Int,
)
