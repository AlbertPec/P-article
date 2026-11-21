package com.example.p_article.data.local.dao

import androidx.room.Dao
import androidx.room.Embedded
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Upsert
import com.example.p_article.data.local.entity.ArticleEntity
import com.example.p_article.data.local.entity.PanelEntity
import com.example.p_article.data.local.entity.ParticleEntity
import com.example.p_article.data.local.entity.ParticleStatusEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ParticleDao {
    @Upsert suspend fun upsertArticle(article: ArticleEntity)
    @Upsert suspend fun upsertParticles(particles: List<ParticleEntity>)
    @Upsert suspend fun upsertPanels(panels: List<PanelEntity>)

    @Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insertArticle(a: ArticleEntity)
    @Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insertParticle(p: ParticleEntity)
    @Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insertPanels(p: List<PanelEntity>)

    @Transaction
    suspend fun saveParticle(p: ParticleEntity, panels: List<PanelEntity>) {
        insertParticle(p)
        insertPanels(panels)
    }

    @Query("SELECT partNo FROM particles WHERE articleId = :articleId")
    suspend fun downloadedParts(articleId: String): List<Int>

    @Query("SELECT id FROM articles")
    suspend fun knownArticleIds(): List<String>

    @Transaction
    suspend fun saveArticleWithParticlesAndPanels(
        a: ArticleEntity,
        ps: List<ParticleEntity>,
        pls: List<PanelEntity>
    ) {
        upsertArticle(a)
        upsertParticles(ps)
        upsertPanels(pls)
    }

    private companion object {
        const val SELECT_PANEL = """
            SELECT pl.*, a.title AS articleTitle, s.status AS status
            FROM panels pl
            JOIN particles p ON p.articleId = pl.articleId AND p.partNo = pl.partNo
            JOIN articles a ON a.id = pl.articleId
            LEFT JOIN particle_status s ON s.articleId = pl.articleId AND s.partNo = pl.partNo
        """
        const val SELECT_PARTICLE = """
            SELECT p.*, a.title AS articleTitle, s.status AS status
            FROM particles p
            JOIN articles a ON a.id = p.articleId
            LEFT JOIN particle_status s ON s.articleId = p.articleId AND s.partNo = p.partNo
        """
    }

    @Query("$SELECT_PANEL WHERE s.status IS NULL OR s.status != 'Hidden' ORDER BY pl.articleId, pl.partNo, pl.position")
    fun observeFeed(): Flow<List<PanelRow>>

    @Query("$SELECT_PARTICLE WHERE p.articleId = :articleId AND p.partNo = :partNo")
    fun observeParticle(articleId: String, partNo: Int): Flow<ParticleRow?>

    @Query("$SELECT_PARTICLE WHERE p.articleId = :articleId AND p.partNo = :partNo")
    suspend fun getByPartNo(articleId: String, partNo: Int): ParticleRow?

    @Query("$SELECT_PANEL WHERE s.status = 'Finished' OR s.status = 'Keep' ORDER BY s.updatedAtMillis DESC")
    fun observeHistory(): Flow<List<PanelRow>>

    @Upsert
    suspend fun upsertStatus(status: ParticleStatusEntity)
}
