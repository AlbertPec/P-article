package com.example.p_article.ui.navigation

import androidx.compose.animation.ExitTransition
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.p_article.PArticleApplication
import com.example.p_article.ui.article.ArticleScreen
import com.example.p_article.ui.feed.FeedScreen
import com.example.p_article.ui.history.HistoryScreen
import com.example.p_article.ui.history.HistoryViewModel
import com.example.p_article.ui.settings.SettingsScreen

private const val FEED = "feed"
private const val ARTICLE = "article/{articleId}/{partNo}"
private const val SETTINGS = "settings"
private const val HISTORY = "history"

@Composable
fun AppNavHost(
    darkMode: Boolean,
    onDarkModeChange: (Boolean) -> Unit,
    serverUrl: String,
    onServerUrlChange: (String) -> Unit,
    navController: NavHostController = rememberNavController(),
) {
    NavHost(navController, startDestination = FEED) {
        composable(FEED) {
            FeedScreen(
                onArticleClick = { articleId, partNo -> navController.navigate("article/$articleId/$partNo") },
                onSettingsClick = { navController.navigate(SETTINGS) { launchSingleTop = true } },
                onHistoryClick = { navController.navigate(HISTORY) { launchSingleTop = true } },
            )
        }
        composable(
            route = ARTICLE,
            arguments = listOf(
                navArgument("articleId") { type = NavType.StringType },
                navArgument("partNo") { type = NavType.IntType },
            ),
            popExitTransition = { ExitTransition.None },
        ) {
            ArticleScreen(onFinished = { navController.popBackStack() })
        }
        composable(SETTINGS) {
            SettingsScreen(
                darkMode = darkMode,
                onDarkModeChange = onDarkModeChange,
                serverUrl = serverUrl,
                onServerUrlChange = onServerUrlChange,
                onBack = { navController.popBackStack() },
            )
        }
        composable(HISTORY) {
            val context = LocalContext.current
            val app = context.applicationContext as PArticleApplication
            val viewModel: HistoryViewModel = viewModel(
                factory = HistoryViewModel.factory(app.container.particleRepository)
            )
            HistoryScreen(
                viewModel = viewModel,
                onOpenArticle = { articleId, partNo -> navController.navigate("article/$articleId/$partNo") },
                onBack = { navController.popBackStack() },
            )
        }
    }
}
