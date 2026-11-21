package com.example.p_article.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.example.p_article.data.local.dao.ArticleDao
import com.example.p_article.data.local.dao.PanelDao
import com.example.p_article.data.local.dao.ParticleDao
import com.example.p_article.data.local.dao.StatusDao
import com.example.p_article.data.local.entity.ArticleEntity
import com.example.p_article.data.local.entity.PanelEntity
import com.example.p_article.data.local.entity.ParticleEntity
import com.example.p_article.data.local.entity.ParticleStatusEntity

@Database(
    entities = [ArticleEntity::class, ParticleEntity::class, PanelEntity::class, ParticleStatusEntity::class],
    version = 2,
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao
    abstract fun panelDao(): PanelDao
    abstract fun statusDao(): StatusDao
    abstract fun particleDao(): ParticleDao
}
