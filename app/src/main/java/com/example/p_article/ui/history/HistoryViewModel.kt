package com.example.p_article.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.p_article.data.HistoryItem
import com.example.p_article.data.repository.ParticleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update

enum class HistoryFilter(val label: String) {
    ALL("All"),
    IN_PROGRESS("In progress"),
    COMPLETED("Completed"),
}

sealed interface HistoryUiState {
    /** First emission from the repository has not arrived yet. */
    data object Loading : HistoryUiState

    /** Nothing has been read yet (independent of the selected filter). */
    data object Empty : HistoryUiState

    /** [items] is already filtered by [filter]; may be empty for a given filter. */
    data class Content(
        val items: List<HistoryItem>,
        val filter: HistoryFilter,
    ) : HistoryUiState
}

class HistoryViewModel(
    private val repository: ParticleRepository,
) : ViewModel() {

    private val filter = MutableStateFlow(HistoryFilter.ALL)

    val uiState: StateFlow<HistoryUiState> =
        combine(repository.observeHistory(), filter) { items, selected ->
            if (items.isEmpty()) {
                HistoryUiState.Empty
            } else {
                HistoryUiState.Content(
                    items = when (selected) {
                        HistoryFilter.ALL -> items
                        HistoryFilter.IN_PROGRESS -> items.filterNot { it.isCompleted }
                        HistoryFilter.COMPLETED -> items.filter { it.isCompleted }
                    },
                    filter = selected,
                )
            }
        }.stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = HistoryUiState.Loading,
        )

    fun onFilterSelected(selected: HistoryFilter) {
        filter.update { selected }
    }

    /** Lowest unread part_no, or 1 when the article is completed. */
    suspend fun getResumePartNo(articleId: String): Int =
        repository.getResumePartNo(articleId)

    companion object {
        fun factory(repository: ParticleRepository): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T =
                    HistoryViewModel(repository) as T
            }
    }
}