package com.example.p_article.data

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import android.util.Log
import com.example.p_article.BuildConfig
import com.example.p_article.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONException
import org.json.JSONObject
import java.io.FileNotFoundException
import java.io.IOException
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URL
import java.net.URLEncoder

class ArticleUploadRepository(context: Context) {
    private val appContext = context.applicationContext
    private val resolver = appContext.contentResolver

    suspend fun fileName(uri: Uri): String = withContext(Dispatchers.IO) {
        resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) cursor.getString(0) else null
        } ?: uri.lastPathSegment.orEmpty()
    }

    /** Uploads a PDF and waits for the server to parse it. Returns the folder it was saved in. */
    suspend fun parse(uri: Uri, fileName: String): String = withContext(Dispatchers.IO) {
        val query = URLEncoder.encode(fileName, "UTF-8")
        val connection = URL("${BuildConfig.PARSER_SERVER_URL}/articles?filename=$query")
            .openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "POST"
            connection.doOutput = true
            connection.setChunkedStreamingMode(0)
            connection.setRequestProperty("Content-Type", "application/pdf")
            connection.connectTimeout = CONNECT_TIMEOUT_MS
            connection.readTimeout = PARSE_TIMEOUT_MS

            try {
                connection.connect()
            } catch (e: IOException) {
                Log.w(TAG, "Connecting to ${BuildConfig.PARSER_SERVER_URL} failed", e)
                throw IOException(appContext.getString(R.string.error_cant_reach_server))
            }

            val input = resolver.openInputStream(uri) ?: throw FileNotFoundException(appContext.getString(R.string.error_file_not_found))
            input.use { it.copyTo(connection.outputStream) }
            connection.outputStream.close()

            if (connection.responseCode in 200..299) {
                val body = connection.inputStream.bufferedReader().use { it.readText() }
                JSONObject(body).getString("folder")
            } else {
                throw IOException(errorMessage(connection))
            }
        } catch (e: SocketTimeoutException) {
            Log.w(TAG, "Uploading $fileName timed out", e)
            throw IOException(appContext.getString(R.string.error_server_timeout))
        } finally {
            connection.disconnect()
        }
    }

    private fun errorMessage(connection: HttpURLConnection): String {
        val body = connection.errorStream?.bufferedReader()?.use { it.readText() }.orEmpty()
        return try {
            JSONObject(body).getString("detail")
        } catch (_: JSONException) {
            appContext.getString(R.string.error_server_returned, connection.responseCode)
        }
    }

    private companion object {
        const val TAG = "ArticleUpload"
        const val CONNECT_TIMEOUT_MS = 10_000
        const val PARSE_TIMEOUT_MS = 15 * 60 * 1000
    }
}
