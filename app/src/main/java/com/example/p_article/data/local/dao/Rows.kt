package com.example.p_article.data.local.dao

import androidx.room.Embedded
import com.example.p_article.data.local.entity.PanelEntity
import com.example.p_article.data.local.entity.ParticleEntity

data class PanelRow(
    @Embedded val panel: PanelEntity,
    val articleTitle: String,
    val status: String?,            // null = never touched = New
)

data class ParticleRow(
    @Embedded val particle: ParticleEntity,
    val articleTitle: String,
    val status: String?,            // null = never touched = New
)

data class HistoryRow(
    val articleId: String,
    val title: String,
    val authors: String,   // via Converters
    val topic: String,
    val particleCount: Int,
    val readCount: Int,
    val lastReadAt: Long
)