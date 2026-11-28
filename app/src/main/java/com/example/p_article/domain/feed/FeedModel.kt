package com.example.p_article.domain.feed

import com.example.p_article.data.ReadingStatus

data class ParticleKey(val articleId: String, val partNo: Int)

data class FeedParticle(
    val key: ParticleKey,
    val status: ReadingStatus,
    val panelIds: List<String>,
)

data class FeedCard(val particle: ParticleKey, val panelId: String) {
    val id get() = "${particle.articleId}-${particle.partNo}-$panelId"
}

data class FeedContext(val sessionSeed: Long)

class ArticleInfo(val parts: List<FeedParticle>) {
    val isStarted = parts.any { it.status == ReadingStatus.Finished }
}