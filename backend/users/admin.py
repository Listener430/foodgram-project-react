from django.contrib import admin

from foodgram.models import (Favorites, Follow, Ingredient, Recipe,
                             Shopping_cart, Tag)

from .models import User

class RecipeAdmin(admin.ModelAdmin):
    list_filter = [
         "author",
         "tag",
    ]
    search_fields = (
        "author",
        "tag",
    )

admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Shopping_cart)
admin.site.register(Favorites)
admin.site.register(Follow)
