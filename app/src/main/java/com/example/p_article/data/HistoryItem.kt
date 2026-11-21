package com.example.p_article.data

data class HistoryItem(
    val articleId: String,
    val title: String,
    val authors: List<String>,
    val topic: String,
    val particleCount: Int,
    val readCount: Int,
    val lastReadAt: Long,
) {
    val progress: Float
        get() = if (particleCount > 0) (readCount.toFloat() / particleCount.toFloat()).coerceIn(0f, 1f) else 0f

    val isCompleted: Boolean
        get() = readCount >= particleCount && particleCount > 0

    val remainingMinutes: Int
        get() = (particleCount - readCount).coerceAtLeast(0)
}
