package com.example.p_article.domain.feed

import com.example.p_article.data.ReadingStatus
import kotlin.random.Random

fun interface ParticleScorer { fun score(p: FeedParticle, a: ArticleInfo, ctx: FeedContext): Double }

class ScoredRanker(private val scorers: List<Pair<ParticleScorer, Double>>) : ParticleRanker {
    override fun rank(current: List<FeedParticle>, articles: Map<String, ArticleInfo>, ctx: FeedContext) =
        current.sortedByDescending { p ->
            val a = articles.getValue(p.key.articleId)
            scorers.sumOf { (s, w) -> w * s.score(p, a, ctx) }
        }
}

val StartedArticle = ParticleScorer { _, a, _ -> if (a.isStarted) 1.0 else 0.0 }
val KeptBoost = ParticleScorer { p, _, _ -> if (p.status == ReadingStatus.Keep) 1.0 else 0.0 }
val Jitter = ParticleScorer { p, _, ctx -> Random(ctx.sessionSeed xor p.key.hashCode().toLong()).nextDouble() }