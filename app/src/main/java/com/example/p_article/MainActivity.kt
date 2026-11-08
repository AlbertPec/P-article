package com.example.p_article

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.p_article.ui.navigation.AppNavHost
import com.example.p_article.ui.settings.SettingsViewModel
import com.example.p_article.ui.theme.P_articleTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val settingsViewModel: SettingsViewModel = viewModel()
            val darkModeSetting by settingsViewModel.darkMode.collectAsStateWithLifecycle()
            val darkMode = darkModeSetting ?: isSystemInDarkTheme()

            P_articleTheme(darkTheme = darkMode) {   // name depends on your generated theme
                AppNavHost(darkMode = darkMode, onDarkModeChange = settingsViewModel::setDarkMode)
            }
        }
    }
}
//
//@Composable
//fun Greeting(name: String, modifier: Modifier = Modifier) {
//    Text(
//        text = "Hello $name!",
//        modifier = modifier
//    )
//}
//
//@Preview(showBackground = true)
//@Composable
//fun GreetingPreview() {
//    P_articleTheme {
//        Greeting("Android")
//    }
//}