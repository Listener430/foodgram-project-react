from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from foodgram.models import Ingredient

User = get_user_model()


class IngredientSearchFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )

    