package com.example.p_article.ui.addarticles

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.ArticleUploadRepository
import com.example.p_article.R
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SelectedFile(val uri: Uri, val name: String)

sealed interface ArticleStatus {
    data object Waiting : ArticleStatus
    data object Parsing : ArticleStatus
    data class Saved(val folder: String) : ArticleStatus
    data class Failed(val message: String) : ArticleStatus
}

data class QueuedArticle(val id: Long, val file: SelectedFile, val status: ArticleStatus)

class AddArticlesViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = ArticleUploadRepository(application)

    private val _pendingFiles = MutableStateFlow<List<SelectedFile>>(emptyList())
    val pendingFiles: StateFlow<List<SelectedFile>> = _pendingFiles.asStateFlow()

    private val _queue = MutableStateFlow<List<QueuedArticle>>(emptyList())
    val queue: StateFlow<List<QueuedArticle>> = _queue.asStateFlow()

    private var nextId = 0L
    private var worker: Job? = null

    fun onFilesPicked(uris: List<Uri>) {
        viewModelScope.launch {
            _pendingFiles.value = uris.map { SelectedFile(it, repo.fileName(it)) }
        }
    }

    fun cancelPending() {
        _pendingFiles.value = emptyList()
    }

    fun confirmPending() {
        val files = _pendingFiles.value
        _pendingFiles.value = emptyList()
        val newArticles = files.map { QueuedArticle(nextId++, it, ArticleStatus.Waiting) }
        if (worker?.isActive == true) {
            // Files added while a batch is running join that batch
            _queue.update { it + newArticles }
        } else {
            _queue.value = newArticles
            worker = viewModelScope.launch { processQueue() }
        }
    }

    private suspend fun processQueue() {
        while (true) {
            val next = _queue.value.firstOrNull { it.status == ArticleStatus.Waiting } ?: return
            setStatus(next.id, ArticleStatus.Parsing)
            val status = try {
                ArticleStatus.Saved(repo.parse(next.file.uri, next.file.name))
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                ArticleStatus.Failed(e.message ?: getApplication<Application>().getString(R.string.error_something_went_wrong))
            }
            setStatus(next.id, status)
        }
    }

    private fun setStatus(id: Long, status: ArticleStatus) {
        _queue.update { queue -> queue.map { if (it.id == id) it.copy(status = status) else it } }
    }
}
