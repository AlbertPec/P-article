package com.example.p_article.ui.navigation

import androidx.activity.ComponentActivity
import androidx.activity.compose.LocalActivity
import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.p_article.ui.addarticles.AddArticlesScreen
import com.example.p_article.ui.article.ArticleScreen
import com.example.p_article.ui.feed.FeedScreen
import com.example.p_article.ui.settings.SettingsScreen

private const val FEED = "feed"
private const val ARTICLE = "article/{articleId}"
private const val SETTINGS = "settings"
private const val ADD_ARTICLES = "add_articles"

@Composable
fun AppNavHost(
    darkMode: Boolean,
    onDarkModeChange: (Boolean) -> Unit,
    navController: NavHostController = rememberNavController(),
) {
    NavHost(navController, startDestination = FEED) {
        composable(FEED) {
            FeedScreen(
                onArticleClick = { id -> navController.navigate("article/$id") },
                onSettingsClick = { navController.navigate(SETTINGS) { launchSingleTop = true } },
                onAddArticlesClick = { navController.navigate(ADD_ARTICLES) { launchSingleTop = true } },
            )
        }
        composable(
            route = ARTICLE,
            arguments = listOf(navArgument("articleId") { type = NavType.IntType }),
        ) {
            ArticleScreen(onBack = { navController.popBackStack() })
        }
        composable(ADD_ARTICLES) {
            AddArticlesScreen(
                onBack = { navController.popBackStack() },
                // Scoped to the activity so the queue keeps running after leaving this screen
                viewModel = viewModel(viewModelStoreOwner = LocalActivity.current as ComponentActivity),
            )
        }
        composable(SETTINGS) {
            SettingsScreen(
                darkMode = darkMode,
                onDarkModeChange = onDarkModeChange,
                onBack = { navController.popBackStack() },
            )
        }
    }
}
