package com.example.p_article.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.p_article.data.local.entity.ArticleEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ArticleDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(article: ArticleEntity)

    @Query("SELECT * FROM articles WHERE id = :id")
    suspend fun get(id: String): ArticleEntity?

    @Query("SELECT * FROM articles ORDER BY title")
    fun observeAll(): Flow<List<ArticleEntity>>

    // sync: which articles do we already have metadata for?
    @Query("SELECT id FROM articles")
    suspend fun knownIds(): List<String>
}