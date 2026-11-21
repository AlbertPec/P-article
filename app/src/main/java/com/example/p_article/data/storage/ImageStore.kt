package com.example.p_article.data.storage

import android.util.Base64
import java.io.File
import java.io.FileOutputStream

class ImageStore(private val root: File) {   // root = filesDir/articles

    fun savePanelImage(articleId: String, partNo: Int, position: Int, base64: String): String {
        val cleanBase64 = if (base64.contains(",")) base64.substringAfter(",") else base64
        val bytes = Base64.decode(cleanBase64, Base64.DEFAULT)
        val dir = File(root, "$articleId/$partNo").apply { mkdirs() }
        val file = File(dir, "panel_$position.jpg")
        FileOutputStream(file).use { it.write(bytes) }
        return "$articleId/$partNo/${file.name}"
    }

    fun saveArticleImages(articleId: String, partNo: Int, images: Map<String, String>) {
        val dir = File(root, "$articleId/$partNo").apply { mkdirs() }
        for ((name, base64) in images) {
            val cleanBase64 = if (base64.contains(",")) base64.substringAfter(",") else base64
            val bytes = Base64.decode(cleanBase64, Base64.DEFAULT)
            val file = File(dir, name)
            FileOutputStream(file).use { it.write(bytes) }
        }
    }

    fun resolve(articleId: String, partNo: Int, name: String): File {
        return File(root, "$articleId/$partNo/$name")
    }

    fun resolvePath(relativePath: String): File {
        return File(root, relativePath)
    }

    fun deleteParticle(articleId: String, partNo: Int) {
        val dir = File(root, "$articleId/$partNo")
        if (dir.exists()) {
            dir.deleteRecursively()
        }
    }
}
