package com.example.p_article

import android.app.Application

class PArticleApplication : Application() {
    val container by lazy { AppContainer(this) }
}
