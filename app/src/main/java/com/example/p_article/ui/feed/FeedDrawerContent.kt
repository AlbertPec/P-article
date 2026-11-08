package com.example.p_article.ui.feed

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AddCircle
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.vectorResource
import androidx.compose.ui.unit.dp
import com.example.p_article.R

@Composable
fun FeedDrawerContent(onSettingsClick: () -> Unit, onItemClick: () -> Unit) {
    ModalDrawerSheet {
        Text("Menu", Modifier.padding(16.dp), style = MaterialTheme.typography.titleLarge)
        listOf(
            Triple("Settings", Icons.Outlined.Settings, onSettingsClick),
            Triple("Add articles", Icons.Outlined.AddCircle, onItemClick),   // TODO: real action later
            Triple("History", ImageVector.vectorResource(R.drawable.ic_history), onItemClick),   // TODO: real action later
        ).forEachIndexed { index, (label, icon, onClick) ->
            if (index > 0) {
                HorizontalDivider(Modifier.padding(NavigationDrawerItemDefaults.ItemPadding))
            }
            NavigationDrawerItem(
                icon = { Icon(icon, contentDescription = null) },
                label = { Text(label) },
                selected = false,
                onClick = onClick,
                modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding),
            )
        }
    }
}