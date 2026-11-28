package com.example.p_article

import android.content.Context
import androidx.room.Room
import com.example.p_article.data.SettingsRepository
import com.example.p_article.data.local.AppDatabase
import com.example.p_article.data.remote.ParticleApi
import com.example.p_article.data.repository.ParticleRepository
import com.example.p_article.data.repository.RoomParticleRepository
import com.example.p_article.data.storage.ImageStore
import com.example.p_article.domain.feed.FeedBuilder
import com.example.p_article.domain.feed.Jitter
import com.example.p_article.domain.feed.KeptBoost
import com.example.p_article.domain.feed.RoundRobinLayout
import com.example.p_article.domain.feed.ScoredRanker
import com.example.p_article.domain.feed.StartedArticle
import java.io.File

class AppContainer(context: Context) {
    private val db = Room.databaseBuilder(context, AppDatabase::class.java, "particles.db")
        .fallbackToDestructiveMigration(true)
        .build()
    val settings = SettingsRepository(context)
    val imageStore = ImageStore(File(context.filesDir, "articles"))
    val feedBuilder = FeedBuilder(
        ranker = ScoredRanker(
            listOf(
                KeptBoost to 3.0,
                StartedArticle to 1.5,
                Jitter to 0.5
            )
        ),
        layout = RoundRobinLayout(),
    )
    val particleRepository: ParticleRepository =
        RoomParticleRepository(
            particleDao = db.particleDao(),
            panelDao = db.panelDao(),
            statusDao = db.statusDao(),
            articleDao = db.articleDao(),
            imageStore = imageStore,
            api = ParticleApi(baseUrl = { settings.serverUrl.value }),
        )
}
