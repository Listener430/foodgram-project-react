from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from foodgram.models import Ingredient, Recipe

User = get_user_model()


class IngredientSearchFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("is_in_shopping_cart", "is_favorited")

    def filter_is_favorited(self, queryset, value):
        if value:
            return queryset.filter(recipe_follower__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        if value:
            return queryset.filter(shopping_cart_follower__user=self.request.user)
        return queryset
