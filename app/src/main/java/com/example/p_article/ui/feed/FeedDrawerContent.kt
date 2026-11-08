package com.example.p_article.ui.feed

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun FeedDrawerContent(onItemClick: () -> Unit) {
    ModalDrawerSheet {
        Text("Menu", Modifier.padding(16.dp), style = MaterialTheme.typography.titleLarge)
        listOf("Profile", "Saved", "Settings").forEach { label ->
            NavigationDrawerItem(
                label = { Text(label) },
                selected = false,
                onClick = onItemClick,   // TODO: real actions later
                modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding),
            )
        }
    }
}