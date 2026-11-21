package com.example.p_article.ui

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat

fun needsLocalNetworkPermission(context: Context): Boolean =
    Build.VERSION.SDK_INT >= 37 &&
        ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_LOCAL_NETWORK) !=
        PackageManager.PERMISSION_GRANTED
