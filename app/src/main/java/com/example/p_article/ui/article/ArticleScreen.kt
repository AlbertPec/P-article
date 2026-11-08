package com.example.p_article.ui.article

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutLinearInEasing
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalWindowInfo
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.example.p_article.data.ReadingStatus
import com.example.p_article.ui.theme.ArticleDeleteButton
import com.example.p_article.ui.theme.ArticleDeleteIcon
import com.example.p_article.ui.theme.ArticleSwipeBackdrop
import com.example.p_article.ui.theme.ArticleSwipeFinished
import com.example.p_article.ui.theme.ArticleSwipeKeep
import com.example.p_article.ui.theme.ArticleSwipeLabel
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.roundToInt

@Composable
fun ArticleScreen(onFinished: () -> Unit, viewModel: ArticleViewModel = viewModel()) {
    val article by viewModel.article.collectAsStateWithLifecycle()
    val scope = rememberCoroutineScope()
    val offsetX = remember { Animatable(0f) }
    val trashProgress = remember { Animatable(0f) }
    var isLeaving by remember { mutableStateOf(false) }

    val screenWidth = LocalWindowInfo.current.containerSize.width.toFloat()
    val threshold = screenWidth * 0.3f

    fun swipeAway(status: ReadingStatus, toRight: Boolean) {
        if (isLeaving) return
        isLeaving = true
        scope.launch {
            offsetX.animateTo(if (toRight) screenWidth * 1.5f else -screenWidth * 1.5f, tween(200))
            viewModel.mark(status)
            onFinished()
        }
    }

    fun trash() {
        if (isLeaving) return
        isLeaving = true
        scope.launch {
            trashProgress.animateTo(1f, tween(350, easing = FastOutLinearInEasing))
            viewModel.mark(ReadingStatus.Hidden)
            onFinished()
        }
    }

    Box(Modifier.fillMaxSize()) {
        val absX = abs(offsetX.value)
        val rawProgress = (absX / threshold).coerceIn(0f, 1f)
        val fadeOut = if (absX > threshold) (1f - (absX - threshold) / (screenWidth * 1.2f - threshold)).coerceIn(0f, 1f) else 1f
        val currentAlpha = rawProgress * fadeOut

        Box(
            Modifier
                .fillMaxSize()
                .background(ArticleSwipeBackdrop)
                .background(
                    if (offsetX.value >= 0) ArticleSwipeFinished.copy(alpha = currentAlpha * 0.8f)
                    else ArticleSwipeKeep.copy(alpha = currentAlpha * 0.8f)
                ),
            contentAlignment = if (offsetX.value >= 0) Alignment.CenterStart else Alignment.CenterEnd,
        ) {
            Text(
                text = if (offsetX.value >= 0) "Finished" else "Keep",
                color = ArticleSwipeLabel.copy(alpha = currentAlpha),
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier.padding(32.dp),
            )
        }

        Surface(
            modifier = Modifier
                .fillMaxSize()
                .offset { IntOffset(offsetX.value.roundToInt(), 0) }
                .graphicsLayer {
                    rotationZ = offsetX.value / screenWidth * 15f + trashProgress.value * 20f
                    val s = 1f - 0.8f * trashProgress.value
                    scaleX = s
                    scaleY = s
                    alpha = 1f - trashProgress.value
                    translationY = trashProgress.value * size.height * 0.25f
                }
                .draggable(
                    orientation = Orientation.Horizontal,
                    state = rememberDraggableState { delta ->
                        scope.launch { offsetX.snapTo(offsetX.value + delta) }
                    },
                    onDragStopped = { velocity ->
                        val x = offsetX.value
                        when {
                            x > threshold || (x > 0 && velocity > 1500f) -> swipeAway(ReadingStatus.Finished, toRight = true)
                            x < -threshold || (x < 0 && velocity < -1500f) -> swipeAway(
                                ReadingStatus.Keep, toRight = false)
                            else -> scope.launch { offsetX.animateTo(0f, spring()) }
                        }
                    },
                ),
        ) {
            article?.let { a ->
                Column(Modifier.verticalScroll(rememberScrollState())) {
                    Box(Modifier.fillMaxWidth()) {
                        AsyncImage(
                            model = a.imageUrl,
                            contentDescription = a.title,
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f),
                        )
                        FilledIconButton(
                            onClick = ::trash,
                            enabled = !isLeaving,
                            colors = IconButtonDefaults.filledIconButtonColors(
                                containerColor = ArticleDeleteButton,
                                contentColor = ArticleDeleteIcon,
                                disabledContainerColor = ArticleDeleteButton,
                                disabledContentColor = ArticleDeleteIcon,
                            ),
                            modifier = Modifier
                                .align(Alignment.TopEnd)
                                .statusBarsPadding()
                                .padding(12.dp)
                                .size(40.dp)
                                .graphicsLayer {
                                    val swipe = (abs(offsetX.value) / threshold).coerceIn(0f, 1f)
                                    alpha = (1f - swipe) * (1f - trashProgress.value)
                                },
                        ) {
                            Icon(Icons.Default.Delete, contentDescription = "Don't show this article")
                        }
                    }
                    Text(a.title, Modifier.padding(16.dp), style = MaterialTheme.typography.headlineSmall)
                    Text(a.content, Modifier.padding(horizontal = 16.dp))
                }
            }
        }
    }
}
