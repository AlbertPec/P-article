package com.example.p_article.data.local.dao

import androidx.room.Dao
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface PanelDao {
    private companion object {
        const val PANEL_SELECT = """
            SELECT pn.*, a.title AS articleTitle, s.status AS status
            FROM panels pn
            JOIN particles p ON p.articleId = pn.articleId AND p.partNo = pn.partNo
            JOIN articles a ON a.id = pn.articleId
            LEFT JOIN particle_status s ON s.articleId = pn.articleId AND s.partNo = pn.partNo
        """
    }

    // Every panel of every non-hidden particle.
    @Query("$PANEL_SELECT WHERE s.status IS NULL OR s.status != 'Hidden' ORDER BY pn.articleId, pn.partNo, pn.position")
    fun observeFeed(): Flow<List<PanelRow>>

    // History: one panel per read/finished/keep particle (the first), newest first.
    @Query("""
        $PANEL_SELECT
        WHERE (s.status = 'Finished' OR s.status = 'Keep' OR s.status = 'Read')
          AND pn.position = (
              SELECT MIN(position) FROM panels
              WHERE articleId = pn.articleId AND partNo = pn.partNo
          )
        ORDER BY s.updatedAtMillis DESC
    """)
    fun observeHistory(): Flow<List<PanelRow>>
}
