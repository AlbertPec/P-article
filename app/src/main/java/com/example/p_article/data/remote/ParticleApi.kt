package com.example.p_article.data.remote

import com.example.p_article.data.remote.dto.ArticleDto
import com.example.p_article.data.remote.dto.ArticleSummaryDto
import com.example.p_article.data.remote.dto.PanelDto
import com.example.p_article.data.remote.dto.ParticleDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

class ParticleApi(private val baseUrl: () -> String) {

    suspend fun articles(): List<ArticleSummaryDto> {
        val array = JSONArray(get("/articles"))
        return List(array.length()) { i ->
            val json = array.getJSONObject(i)
            ArticleSummaryDto(id = json.getString("id"), particleCount = json.getInt("particle_count"))
        }
    }

    suspend fun article(articleId: String): ArticleDto {
        val json = JSONObject(get("/articles/$articleId"))
        return ArticleDto(
            id = json.getString("id"),
            title = json.getString("title"),
            authors = json.getJSONArray("authors").toStringList(),
            affiliations = json.getJSONArray("affiliations").toStringList(),
            topic = json.getString("topic"),
            particleCount = json.getInt("particle_count"),
        )
    }

    suspend fun panels(articleId: String, partNo: Int): List<PanelDto> {
        val array = JSONArray(get("/articles/$articleId/particles/$partNo/panels"))
        return List(array.length()) { i ->
            val json = array.getJSONObject(i)
            PanelDto(header = json.getString("header"), image = json.getString("image"))
        }
    }

    suspend fun particle(articleId: String, partNo: Int): ParticleDto {
        val json = JSONObject(get("/articles/$articleId/particles/$partNo"))
        val images = json.getJSONObject("images")
        return ParticleDto(
            content = json.getString("content"),
            images = images.keys().asSequence().associateWith { images.getString(it) },
        )
    }

    private suspend fun get(path: String): String = withContext(Dispatchers.IO) {
        val connection = URL("${baseUrl()}$path").openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = CONNECT_TIMEOUT_MS
            connection.readTimeout = READ_TIMEOUT_MS
            if (connection.responseCode in 200..299) {
                connection.inputStream.bufferedReader().use { it.readText() }
            } else {
                throw IOException("GET $path failed: ${errorDetail(connection)}")
            }
        } finally {
            connection.disconnect()
        }
    }

    private fun errorDetail(connection: HttpURLConnection): String {
        val body = connection.errorStream?.bufferedReader()?.use { it.readText() }.orEmpty()
        return try {
            JSONObject(body).getString("detail")
        } catch (_: JSONException) {
            "HTTP ${connection.responseCode}"
        }
    }

    private fun JSONArray.toStringList(): List<String> = List(length()) { getString(it) }

    private companion object {
        const val CONNECT_TIMEOUT_MS = 10_000
        const val READ_TIMEOUT_MS = 30_000
    }
}
