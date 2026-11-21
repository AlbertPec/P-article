package com.example.p_article.data.local

import androidx.room.TypeConverter

class Converters {
    @TypeConverter
    fun fromList(v: List<String>): String = v.joinToString("|||")
    @TypeConverter
    fun toList(v: String): List<String> = if (v.isEmpty()) emptyList() else v.split("|||")
}
