package com.example.p_article.data.repository

import com.example.p_article.data.Panel
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import kotlinx.coroutines.flow.Flow

interface ParticleRepository {
    fun feed(): Flow<List<Panel>>
    fun particle(articleId: String, partNo: Int): Flow<Particle?>
    fun history(): Flow<List<Panel>>
    suspend fun nextParticle(current: Particle): Particle?
    suspend fun setStatus(articleId: String, partNo: Int, status: ReadingStatus)
    suspend fun sync(): Result<Unit>
}
