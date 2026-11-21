package com.example.p_article.ui.navigation

import androidx.compose.animation.ExitTransition
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.p_article.ui.article.ArticleScreen
import com.example.p_article.ui.feed.FeedScreen
import com.example.p_article.ui.settings.SettingsScreen

private const val FEED = "feed"
private const val ARTICLE = "article/{articleId}/{partNo}"
private const val SETTINGS = "settings"

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
    }
}
