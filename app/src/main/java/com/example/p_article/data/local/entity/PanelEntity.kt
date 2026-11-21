package com.example.p_article.data.local.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "panels",
    foreignKeys = [ForeignKey(
        entity = ParticleEntity::class,
        parentColumns = ["articleId", "partNo"], childColumns = ["articleId", "partNo"],
        onDelete = ForeignKey.CASCADE,
    )],
    indices = [Index(value = ["articleId", "partNo", "position"], unique = true)],
)
data class PanelEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val articleId: String,
    val partNo: Int,
    val position: Int,                // order in the server's list
    val header: String,
    val imagePath: String,
)
