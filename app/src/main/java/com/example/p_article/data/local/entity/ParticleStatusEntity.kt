package com.example.p_article.data.local.entity

import androidx.room.Entity

@Entity(tableName = "particle_status", primaryKeys = ["articleId", "partNo"])
data class ParticleStatusEntity(
    val articleId: String,
    val partNo: Int,
    val status: String,
    val updatedAtMillis: Long,
)
