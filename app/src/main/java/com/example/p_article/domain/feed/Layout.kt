package com.example.p_article.domain.feed

import kotlin.random.Random

class RoundRobinLayout(private val maxCardsPerParticle: Int = Int.MAX_VALUE) : CardLayout {
    override fun layout(ranked: List<FeedParticle>, ctx: FeedContext): List<FeedCard> {
        val panels = ranked.associate { p ->
            p.key to p.panelIds.shuffled(Random(ctx.sessionSeed xor p.key.hashCode().toLong())).take(maxCardsPerParticle)
        }
        val rounds = panels.values.maxOfOrNull { it.size } ?: 0
        return (0 until rounds).flatMap { r ->
            ranked.mapNotNull { p -> panels.getValue(p.key).getOrNull(r)?.let { FeedCard(p.key, it) } }
        }
    }
}