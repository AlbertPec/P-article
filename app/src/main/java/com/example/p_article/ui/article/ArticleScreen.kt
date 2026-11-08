package com.example.p_article.ui.article

import androidx.compose.animation.core.Animatable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalWindowInfo
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.example.p_article.data.SwipeDecision
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.roundToInt

@Composable
fun ArticleScreen(onFinished: () -> Unit, viewModel: ArticleViewModel = viewModel()) {
    val article by viewModel.article.collectAsStateWithLifecycle()
    val scope = rememberCoroutineScope()
    val offsetX = remember { Animatable(0f) }

    val screenWidth = LocalWindowInfo.current.containerSize.width.toFloat()
    val threshold = screenWidth * 0.3f

    fun flyOff(decision: SwipeDecision) = scope.launch {
        val target = if (decision == SwipeDecision.Finished) screenWidth * 1.5f else -screenWidth * 1.5f
        offsetX.animateTo(target, tween(200))
        viewModel.mark(decision)
        onFinished()
    }

    Box(Modifier.fillMaxSize()) {
        val progress = (offsetX.value / threshold).coerceIn(-1f, 1f)
        Box(
            Modifier
                .fillMaxSize()
                .background(
                    if (progress >= 0) Color(0xFF2E7D32).copy(alpha = progress * 0.8f)
                    else Color(0xFFECCE2A).copy(alpha = -progress * 0.8f)
                ),
            contentAlignment = if (progress >= 0) Alignment.CenterStart else Alignment.CenterEnd,
        ) {
            Text(
                text = if (progress >= 0) "Finished" else "Keep",
                color = Color.White.copy(alpha = abs(progress)),
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier.padding(32.dp),
            )
        }

        Surface(
            modifier = Modifier
                .fillMaxSize()
                .offset { IntOffset(offsetX.value.roundToInt(), 0) }
                .graphicsLayer { rotationZ = offsetX.value / screenWidth * 15f }
                .draggable(
                    orientation = Orientation.Horizontal,
                    state = rememberDraggableState { delta ->
                        scope.launch { offsetX.snapTo(offsetX.value + delta) }
                    },
                    onDragStopped = { velocity ->
                        val x = offsetX.value
                        when {
                            x > threshold || (x > 0 && velocity > 1500f) -> flyOff(SwipeDecision.Finished)
                            x < -threshold || (x < 0 && velocity < -1500f) -> flyOff(SwipeDecision.Keep)
                            else -> scope.launch { offsetX.animateTo(0f, spring()) }
                        }
                    },
                ),
        ) {
            article?.let { a ->
                Column(Modifier.verticalScroll(rememberScrollState())) {
                    AsyncImage(
                        model = a.imageUrl,
                        contentDescription = a.title,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f),
                    )
                    Text(a.title, Modifier.padding(16.dp), style = MaterialTheme.typography.headlineSmall)
                    Text(a.content, Modifier.padding(horizontal = 16.dp))
                }
            }
        }
    }
}