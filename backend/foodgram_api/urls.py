from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionListViewSet,
    SubscriptionViewSet,
    TagViewSet
)

router = routers.DefaultRouter()
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)
router.register(r"tags", TagViewSet)


urlpatterns = [
    path("", include(router.urls), name="api_urls"),
    path(
        "users/<int:user_id>/subscribe/",
        SubscriptionViewSet.as_view(
            {
                "post": "create_subscription",
                "delete": "delete_subscription",
            }
        ),
        name="subscribe",
    ),
    path(
        "users/subscriptions/",
        SubscriptionListViewSet.as_view({"get": "subscriptions"}),
        name="subscriptions",
    ),
]
