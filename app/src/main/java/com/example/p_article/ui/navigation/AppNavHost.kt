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

private const val FEED = "feed"
private const val ARTICLE = "article/{articleId}"

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController, startDestination = FEED) {
        composable(FEED) {
            FeedScreen(onArticleClick = { id -> navController.navigate("article/$id") })
        }
        composable(
            route = ARTICLE,
            arguments = listOf(navArgument("articleId") { type = NavType.IntType }),
            popExitTransition = { ExitTransition.None },
        ) {
            ArticleScreen(onFinished = { navController.popBackStack() })
        }
    }
}
