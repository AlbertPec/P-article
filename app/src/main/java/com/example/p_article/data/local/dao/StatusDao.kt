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

    @Query("""
        SELECT a.id AS articleId, a.title, a.authors, a.topic, a.particleCount,
               COUNT(s.partNo) AS readCount, MAX(s.updatedAtMillis) AS lastReadAt
        FROM articles a
        JOIN particle_status s ON s.articleId = a.id AND (s.status = 'Finished' OR s.status = 'Keep' OR s.status = 'Read' OR s.status = 'READ')
        GROUP BY a.id
        ORDER BY lastReadAt DESC
    """)
    fun observeHistory(): Flow<List<HistoryRow>>

    @Query("SELECT partNo FROM particle_status WHERE articleId = :articleId AND (status = 'Finished' OR status = 'Keep' OR status = 'Read' OR status = 'READ')")
    suspend fun getReadPartNos(articleId: String): List<Int>
}