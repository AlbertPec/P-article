package com.example.p_article.data.local.entity

import androidx.room.Entity
import androidx.room.ForeignKey

@Entity(
    tableName = "particles",
    primaryKeys = ["articleId", "partNo"],
    foreignKeys = [ForeignKey(
        entity = ArticleEntity::class,
        parentColumns = ["id"], childColumns = ["articleId"],
        onDelete = ForeignKey.CASCADE,
    )],
)
data class ParticleEntity(
    val articleId: String,
    val partNo: Int,
    val content: String,
)
