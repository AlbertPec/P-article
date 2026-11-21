package com.example.p_article.data.local.dao

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import com.example.p_article.data.local.entity.ParticleStatusEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface StatusDao {
    @Upsert
    suspend fun upsert(status: ParticleStatusEntity)

    @Query("SELECT status FROM particle_status WHERE articleId = :articleId AND partNo = :partNo")
    suspend fun get(articleId: String, partNo: Int): String?

    // input for POST /recommendations
    @Query("SELECT DISTINCT articleId FROM particle_status WHERE status = 'Read'")
    suspend fun readArticleIds(): List<String>

    // statistics: how many particles were read, and when
    @Query("SELECT updatedAtMillis FROM particle_status WHERE status = 'Read' ORDER BY updatedAtMillis")
    fun observeReadTimestamps(): Flow<List<Long>>
}