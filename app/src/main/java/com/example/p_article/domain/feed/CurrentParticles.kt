package com.example.p_article.domain.feed

import com.example.p_article.data.ReadingStatus

object CurrentParticles {
    fun select(input: List<FeedParticle>): List<FeedParticle> =
        input.groupBy { it.key.articleId }.values.mapNotNull { parts ->
            if (parts.any { it.status == ReadingStatus.Hidden }) null
            else parts.sortedBy { it.key.partNo }.firstOrNull { it.status != ReadingStatus.Finished }
        }
}