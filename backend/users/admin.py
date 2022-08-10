from django.contrib import admin
from foodgram.models import (Favorite, Follow, Ingredient, Recipe,
                             ShoppingCart, Tag)

from .models import User


class RecipeAdmin(admin.ModelAdmin):
    list_filter = [
         "author",
         "tags",
    ]
    search_fields = (
        "author",
        "tags",
    )

admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(Follow)


