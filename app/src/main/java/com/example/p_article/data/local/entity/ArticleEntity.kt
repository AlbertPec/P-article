package com.example.p_article.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val authors: List<String>,        // needs the TypeConverter back
    val affiliations: List<String>,
    val topic: String,
    val particleCount: Int,
)
