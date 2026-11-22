package com.example.p_article.domain.feed

fun interface ParticleRanker { fun rank(current: List<FeedParticle>, articles: Map<String, ArticleInfo>, ctx: FeedContext): List<FeedParticle> }
fun interface CardLayout { fun layout(ranked: List<FeedParticle>, ctx: FeedContext): List<FeedCard> }

class FeedBuilder(private val ranker: ParticleRanker, private val layout: CardLayout) {
    fun currentKeys(input: List<FeedParticle>): Set<ParticleKey> =
        CurrentParticles.select(input).filter { it.panelIds.isNotEmpty() }.map { it.key }.toSet()

    fun build(input: List<FeedParticle>, ctx: FeedContext): List<FeedCard> {
        val articles = input.groupBy { it.key.articleId }.mapValues { ArticleInfo(it.value) }
        val current = CurrentParticles.select(input).filter { it.panelIds.isNotEmpty() }
        return layout.layout(ranker.rank(current, articles, ctx), ctx)
    }
}