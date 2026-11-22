package com.example.p_article.data

data class Particle(
    val articleId: String,          // link to the parent
    val partNo: Int,                // 1-based, as on the server
    val articleTitle: String,
    val content: String,            // Markdown
    val imagePath: String = "",     // path to panel/cover image
    val status: ReadingStatus = ReadingStatus.New,
    val images: Map<String, String> = emptyMap(),
)

val MARKDOWN_IMAGE = Regex("""!\[([^\]]*)\]\(([^)\s]+)\)""")
