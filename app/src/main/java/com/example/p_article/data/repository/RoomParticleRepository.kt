package com.example.p_article.data.repository

import android.util.Log
import com.example.p_article.data.HistoryItem
import com.example.p_article.data.MARKDOWN_IMAGE
import com.example.p_article.data.Panel
import com.example.p_article.data.Particle
import com.example.p_article.data.ReadingStatus
import com.example.p_article.data.local.dao.ArticleDao
import com.example.p_article.data.local.dao.PanelDao
import com.example.p_article.data.local.dao.PanelRow
import com.example.p_article.data.local.dao.ParticleDao
import com.example.p_article.data.local.dao.ParticleRow
import com.example.p_article.data.local.dao.StatusDao
import com.example.p_article.data.local.entity.ArticleEntity
import com.example.p_article.data.local.entity.PanelEntity
import com.example.p_article.data.local.entity.ParticleEntity
import com.example.p_article.data.local.entity.ParticleStatusEntity
import com.example.p_article.data.remote.ParticleApi
import com.example.p_article.data.storage.ImageStore
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlin.random.Random

class RoomParticleRepository(
    private val particleDao: ParticleDao,
    private val panelDao: PanelDao,
    private val statusDao: StatusDao,
    private val articleDao: ArticleDao,
    private val imageStore: ImageStore,
    private val api: ParticleApi,
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

    override fun observeHistory(): Flow<List<HistoryItem>> =
        statusDao.observeHistory().map { rows ->
            rows.map { row ->
                HistoryItem(
                    articleId = row.articleId,
                    title = row.title,
                    authors = if (row.authors.isEmpty()) emptyList() else row.authors.split("|||"),
                    topic = row.topic,
                    particleCount = row.particleCount,
                    readCount = row.readCount,
                    lastReadAt = row.lastReadAt,
                )
            }
        }

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

    override suspend fun getResumePartNo(articleId: String): Int {
        val article = articleDao.get(articleId) ?: return 1
        val readParts = statusDao.getReadPartNos(articleId).toSet()
        for (i in 1..article.particleCount) {
            if (i !in readParts) {
                return i
            }
        }
        return 1
    }

    override suspend fun sync(): Result<Unit> = try {
        val knownArticles = particleDao.knownArticleIds().toSet()
        for (summary in api.articles()) {
            if (summary.id !in knownArticles) {
                val article = api.article(summary.id)
                particleDao.upsertArticle(
                    ArticleEntity(
                        id = article.id,
                        title = article.title,
                        authors = article.authors,
                        affiliations = article.affiliations,
                        topic = article.topic,
                        particleCount = article.particleCount,
                    )
                )
            }
            val downloaded = particleDao.downloadedParts(summary.id).toSet()
            for (partNo in 1..summary.particleCount) {
                if (partNo !in downloaded) downloadParticle(summary.id, partNo)
            }
        }
        Result.success(Unit)
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        Log.w(TAG, "Sync failed", e)
        Result.failure(e)
    }

    private suspend fun downloadParticle(articleId: String, partNo: Int) {
        val panels = api.panels(articleId, partNo)
        val particle = api.particle(articleId, partNo)
        imageStore.saveArticleImages(articleId, partNo, particle.images)
        val panelEntities = panels.mapIndexed { position, panel ->
            PanelEntity(
                articleId = articleId,
                partNo = partNo,
                position = position,
                header = panel.header,
                imagePath = imageStore.savePanelImage(articleId, partNo, position, panel.image),
            )
        }
        particleDao.saveParticle(ParticleEntity(articleId, partNo, particle.content), panelEntities)
    }

    private fun ParticleRow.toParticle() = Particle(
        articleId = particle.articleId,
        partNo = particle.partNo,
        articleTitle = articleTitle,
        content = particle.content,
        status = status.toReadingStatus(),
        images = MARKDOWN_IMAGE.findAll(particle.content).associate { match ->
            val name = match.groupValues[2]
            name to imageStore.resolve(particle.articleId, particle.partNo, name).absolutePath
        },
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

private const val TAG = "ParticleSync"

private fun String?.toReadingStatus(): ReadingStatus =
    this?.let { name -> ReadingStatus.entries.firstOrNull { it.name == name } }
        ?: ReadingStatus.New
