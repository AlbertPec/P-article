package com.example.p_article.data.repository

import com.example.p_article.data.HistoryItem
import com.example.p_article.data.Panel
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.update

class FakeParticleRepository : ParticleRepository {
    private val statuses = MutableStateFlow<Map<String, ReadingStatus>>(emptyMap())

    private fun key(articleId: String, partNo: Int) = "${articleId}_$partNo"

    private val fakeParticles = List(20) { i ->
        val articleId = "uuid-${i / 3}"
        val partNo = (i % 3) + 1
        Particle(
            articleId = articleId,
            partNo = partNo,
            articleTitle = "Article Title #${i / 3}",
            content = "This is the content of particle #$i. Lorem ipsum dolor sit amet...",
        )
    }

    private val fakePanels = List(20) { i ->
        val articleId = "uuid-${i / 3}"
        val partNo = (i % 3) + 1
        Panel(
            articleId = articleId,
            partNo = partNo,
            articleTitle = "Article Title #${i / 3}",
            header = "Section Header $i",
            imagePath = "",
        )
    }

    private val particlesFlow = MutableStateFlow(fakeParticles)
    private val panelsFlow = MutableStateFlow(fakePanels)

    override fun feed(): Flow<List<Panel>> {
        return panelsFlow.combine(statuses) { panels, statusMap ->
            panels.filter { p ->
                val status = statusMap[key(p.articleId, p.partNo)] ?: ReadingStatus.New
                status != ReadingStatus.Hidden
            }.map { p ->
                p.copy(status = statusMap[key(p.articleId, p.partNo)] ?: ReadingStatus.New)
            }
        }
    }

    override fun particle(articleId: String, partNo: Int): Flow<Particle?> {
        return particlesFlow.combine(statuses) { particles, statusMap ->
            particles.find { it.articleId == articleId && it.partNo == partNo }?.copy(
                status = statusMap[key(articleId, partNo)] ?: ReadingStatus.New
            )
        }
    }

    override fun history(): Flow<List<Panel>> {
        return panelsFlow.combine(statuses) { panels, statusMap ->
            panels.filter { p ->
                val st = statusMap[key(p.articleId, p.partNo)]
                st == ReadingStatus.Finished || st == ReadingStatus.Keep
            }.map { p ->
                p.copy(status = statusMap[key(p.articleId, p.partNo)] ?: ReadingStatus.New)
            }
        }
    }

    override fun observeHistory(): Flow<List<HistoryItem>> {
        return flowOf(
            listOf(
                HistoryItem(
                    articleId = "uuid-0",
                    title = "Sample Article Title",
                    authors = listOf("Author One", "Author Two"),
                    topic = "Technology",
                    particleCount = 3,
                    readCount = 2,
                    lastReadAt = System.currentTimeMillis(),
                )
            )
        )
    }

    override suspend fun nextParticle(current: Particle): Particle? {
        val currentList = particlesFlow.value
        val currentIndex = currentList.indexOfFirst { it.articleId == current.articleId && it.partNo == current.partNo }
        if (currentIndex in 0 until currentList.size - 1) {
            return currentList[currentIndex + 1]
        }
        return null
    }

    override suspend fun setStatus(articleId: String, partNo: Int, status: ReadingStatus) {
        statuses.update { it + (key(articleId, partNo) to status) }
    }

    override suspend fun getResumePartNo(articleId: String): Int {
        return 1
    }

    override suspend fun sync(): Result<Unit> {
        return Result.success(Unit)
    }
}
