package com.example.p_article.data.repository

import com.example.p_article.data.Panel
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import com.example.p_article.data.local.dao.PanelDao
import com.example.p_article.data.local.dao.PanelRow
import com.example.p_article.data.local.dao.ParticleDao
import com.example.p_article.data.local.dao.ParticleRow
import com.example.p_article.data.local.dao.StatusDao
import com.example.p_article.data.local.entity.ParticleStatusEntity
import com.example.p_article.data.storage.ImageStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlin.random.Random

class RoomParticleRepository(
    private val particleDao: ParticleDao,
    private val panelDao: PanelDao,
    private val statusDao: StatusDao,
    private val imageStore: ImageStore,
) : ParticleRepository {
    private val sessionSeed = Random.nextLong()

    override fun feed(): Flow<List<Panel>> =
        panelDao.observeFeed().map { rows ->
            rows.groupBy { it.panel.articleId to it.panel.partNo }
                .map { (key, group) ->
                    // the client chooses which panel of a particle is shown
                    group[Random(sessionSeed + key.hashCode()).nextInt(group.size)].toPanel()
                }
        }

    override fun history(): Flow<List<Panel>> =
        panelDao.observeHistory().map { rows -> rows.map { it.toPanel() } }

    override fun particle(articleId: String, partNo: Int): Flow<Particle?> =
        particleDao.observeParticle(articleId, partNo).map { it?.toParticle() }

    override suspend fun nextParticle(current: Particle): Particle? =
        particleDao.getByPartNo(current.articleId, current.partNo + 1)?.toParticle()

    override suspend fun setStatus(articleId: String, partNo: Int, status: ReadingStatus) {
        statusDao.upsert(
            ParticleStatusEntity(
                articleId = articleId,
                partNo = partNo,
                status = status.name,
                updatedAtMillis = System.currentTimeMillis(),
            )
        )
        if (status == ReadingStatus.Hidden) {
            imageStore.deleteParticle(articleId, partNo)
        }
    }

    override suspend fun sync(): Result<Unit> = Result.success(Unit)

    private fun ParticleRow.toParticle() = Particle(
        articleId = particle.articleId,
        partNo = particle.partNo,
        articleTitle = articleTitle,
        content = particle.content,
        status = status.toReadingStatus(),
    )

    private fun PanelRow.toPanel() = Panel(
        articleId = panel.articleId,
        partNo = panel.partNo,
        articleTitle = articleTitle,
        header = panel.header,
        imagePath = imageStore.resolvePath(panel.imagePath).absolutePath,
        status = status.toReadingStatus(),
    )
}

private fun String?.toReadingStatus(): ReadingStatus =
    this?.let { name -> ReadingStatus.entries.firstOrNull { it.name == name } }
        ?: ReadingStatus.New
