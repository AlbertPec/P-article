package com.example.p_article.ui.history


import android.text.format.DateUtils
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.p_article.data.HistoryItem
import com.example.p_article.ui.theme.P_articleTheme

/**
 * Single row of the history list: one article with reading progress.
 *
 * Expects [HistoryItem] (data/HistoryItem.kt) with:
 *  - articleId: String, title: String, authors: List<String>, topic: String
 *  - particleCount: Int, readCount: Int, lastReadAt: Long (epoch millis)
 *  - computed: progress: Float (0f..1f), isCompleted: Boolean, remainingMinutes: Int
 *
 * Hardcoded strings should be moved to strings.xml (plurals for "particles").
 */
@Composable
fun HistoryItemCard(
    item: HistoryItem,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val lastRead = remember(item.lastReadAt) { formatLastRead(context, item.lastReadAt) }
    val progressDescription = "${item.readCount} of ${item.particleCount} particles read"

    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {

            // Topic + completed badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = item.topic.uppercase(),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.primary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false),
                )
                if (item.isCompleted) {
                    CompletedBadge()
                }
            }

            Spacer(Modifier.height(6.dp))

            Text(
                text = item.title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )

            if (item.authors.isNotEmpty()) {
                Spacer(Modifier.height(2.dp))
                Text(
                    text = item.authors.joinToString(", "),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }

            Spacer(Modifier.height(12.dp))

            LinearProgressIndicator(
                progress = { item.progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .semantics { contentDescription = progressDescription },
                color = if (item.isCompleted) {
                    MaterialTheme.colorScheme.tertiary
                } else {
                    MaterialTheme.colorScheme.primary
                },
                trackColor = MaterialTheme.colorScheme.surface,
            )

            Spacer(Modifier.height(8.dp))

            // "3 / 7 particles"  ·····  "~20 min left"
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = "${item.readCount} / ${item.particleCount} particles",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (!item.isCompleted) {
                    Text(
                        text = "~${item.remainingMinutes} min left",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            Spacer(Modifier.height(4.dp))

            Text(
                text = "Last read: $lastRead",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
            )
        }
    }
}

@Composable
private fun CompletedBadge() {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = Icons.Filled.CheckCircle,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.tertiary,
            modifier = Modifier.size(16.dp),
        )
        Text(
            text = "Completed",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.tertiary,
            modifier = Modifier.padding(start = 4.dp),
        )
    }
}

/** "Today", "Yesterday", otherwise e.g. "12 Nov 2026". Works on API 24 (no java.time). */
private fun formatLastRead(context: android.content.Context, millis: Long): String =
    when {
        DateUtils.isToday(millis) -> "Today"
        DateUtils.isToday(millis + DateUtils.DAY_IN_MILLIS) -> "Yesterday"
        else -> DateUtils.formatDateTime(
            context,
            millis,
            DateUtils.FORMAT_SHOW_DATE or DateUtils.FORMAT_ABBREV_MONTH or DateUtils.FORMAT_SHOW_YEAR,
        )
    }

@Preview(showBackground = true)
@Composable
private fun HistoryItemCardInProgressPreview() {
    P_articleTheme {
        HistoryItemCard(
            item = HistoryItem(
                articleId = "3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71",
                title = "Attention Is All You Need: Rethinking Sequence Transduction",
                authors = listOf("A. Vaswani", "N. Shazeer", "N. Parmar"),
                topic = "Machine learning",
                particleCount = 7,
                readCount = 3,
                lastReadAt = System.currentTimeMillis() - DateUtils.DAY_IN_MILLIS,
            ),
            onClick = {},
            modifier = Modifier.padding(16.dp),
        )
    }
}

@Preview(showBackground = true)
@Composable
private fun HistoryItemCardCompletedPreview() {
    P_articleTheme {
        HistoryItemCard(
            item = HistoryItem(
                articleId = "9c7e1a2d-5b3f-4c8e-a6d0-1f4b7e9c2a35",
                title = "Short article",
                authors = emptyList(),
                topic = "Biology",
                particleCount = 4,
                readCount = 4,
                lastReadAt = System.currentTimeMillis(),
            ),
            onClick = {},
            modifier = Modifier.padding(16.dp),
        )
    }
}