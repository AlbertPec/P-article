package com.example.p_article

import android.content.Context
import androidx.room.Room
import com.example.p_article.data.SettingsRepository
import com.example.p_article.data.local.AppDatabase
import com.example.p_article.data.remote.ParticleApi
import com.example.p_article.data.repository.ParticleRepository
import com.example.p_article.data.repository.RoomParticleRepository
import com.example.p_article.data.storage.ImageStore
import java.io.File

class AppContainer(context: Context) {
    private val db = Room.databaseBuilder(context, AppDatabase::class.java, "particles.db")
        .fallbackToDestructiveMigration(true)
        .build()
    val settings = SettingsRepository(context)
    val imageStore = ImageStore(File(context.filesDir, "articles"))
    val particleRepository: ParticleRepository =
        RoomParticleRepository(
            particleDao = db.particleDao(),
            panelDao = db.panelDao(),
            statusDao = db.statusDao(),
            imageStore = imageStore,
            api = ParticleApi(baseUrl = { settings.serverUrl.value }),
        )
}
