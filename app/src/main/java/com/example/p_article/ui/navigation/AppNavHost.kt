package com.example.p_article.ui.navigation

import androidx.activity.ComponentActivity
import androidx.activity.compose.LocalActivity
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
import com.example.p_article.ParticleApplication
import com.example.p_article.ui.addarticles.AddArticlesScreen
import com.example.p_article.ui.article.ArticleScreen
import com.example.p_article.ui.feed.FeedScreen
import com.example.p_article.ui.history.HistoryScreen
import com.example.p_article.ui.history.HistoryViewModel
import com.example.p_article.ui.settings.SettingsScreen

private const val FEED = "feed"
private const val ARTICLE = "article/{articleId}/{partNo}"
private const val SETTINGS = "settings"
private const val ADD_ARTICLES = "add_articles"
private const val HISTORY = "history"

@Composable
fun AppNavHost(
    darkMode: Boolean,
    onDarkModeChange: (Boolean) -> Unit,
    navController: NavHostController = rememberNavController(),
) {
    NavHost(navController, startDestination = FEED) {
        composable(FEED) {
            FeedScreen(
                onArticleClick = { articleId, partNo -> navController.navigate("article/$articleId/$partNo") },
                onSettingsClick = { navController.navigate(SETTINGS) { launchSingleTop = true } },
                onAddArticlesClick = { navController.navigate(ADD_ARTICLES) { launchSingleTop = true } },
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
        composable(HISTORY) {
            val context = LocalContext.current
            val app = context.applicationContext as ParticleApplication
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
