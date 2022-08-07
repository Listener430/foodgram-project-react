from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, MySubscriptionViewSet, RecipeViewSet,
                    SubscriptionViewSet)

router = routers.DefaultRouter()
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)


urlpatterns = [
    path("", include(router.urls), name="api_urls"),
    path(
        "users/<user_id>/subscribe/",
        SubscriptionViewSet.as_view({"get": "list", "post": "create_subscription", "delete": "delete_subscription"}),
    ),
    path(
        "users/subscriptions/",
        MySubscriptionViewSet.as_view({"get": "subscriptions"}),
    ),
]
