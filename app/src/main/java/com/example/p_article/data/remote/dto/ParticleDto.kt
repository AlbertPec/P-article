package com.example.p_article.data.remote.dto

data class PanelDto(
    val header: String,
    val image: String,
)

data class ParticleDto(
    val content: String,
    val images: Map<String, String>,
)
