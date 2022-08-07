import io

import pandas
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.models import (Favorites, Follow, Ingredient,
                             IngredientRecipeAmount, Recipe, Shopping_cart,
                             Tag)
from users.models import User

from .filters import IngredientSearchFilter
from .mixins import ListMixin
from .serializers import (IngredientSerializer, MySubcriptionsSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SubcriptionsSerializer)


class IngredientViewSet(ListMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = IngredientSearchFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if not Favorites.objects.filter(recipe=recipe, user=request.user).exists():
                Favorites.objects.create(recipe=recipe, user=request.user)
                return Response(
                    RecipeShortSerializer(recipe).data, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Рецепт есть в списке фаворитов"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            if Favorites.objects.filter(recipe=recipe, user=request.user).exists():
                Favorites.objects.filter(recipe=recipe, user=request.user).delete()
                return Response(
                    {"detail": "Удалили из списка фаворитов"}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Рецепта нет в списке фаворитов"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if not Shopping_cart.objects.filter(
                recipe=recipe, user=request.user
            ).exists():
                Shopping_cart.objects.create(recipe=recipe, user=request.user)
                return Response(
                    RecipeShortSerializer(recipe).data, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Рецепт уже есть в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            if Shopping_cart.objects.filter(recipe=recipe, user=request.user).exists():
                Shopping_cart.objects.filter(recipe=recipe, user=request.user).delete()
                return Response(
                    {"detail": "Удалили из списка покупок"}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def download_shopping_cart(self, request):
        """в постмане чтобы посмотреть надо выбрать Save Response, Save to file"""
        queryset1 = (
            IngredientRecipeAmount.objects.filter(
                recipe__shopping_following_recipe__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        data = list(queryset1)
        data_frame = pandas.DataFrame(data)
        data_frame.rename(
            columns={
                "ingredient__name": "ингредиент",
                "ingredient__measurement_unit": "ед.изм",
                "amount": "кол-во",
            },
            inplace=True,
        )
        excel_file = io.BytesIO()

        writer = pandas.ExcelWriter(excel_file, engine="xlsxwriter")
        data_frame.to_excel(writer, sheet_name="список покупок", index=False)
        writer.save()
        writer.close()

        excel_file.seek(0)
        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=shopping_list.xlsx"
        return response


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubcriptionsSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(id=self.kwargs.get("user_id"))

    def create_subscription(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("user_id"))
        if request.method == "POST":
            if not Follow.objects.filter(user=request.user, author=author).exists():
                Follow.objects.create(user=request.user, author=author)
                return Response(SubcriptionsSerializer(author).data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,)

    def delete_subscription(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("user_id"))
        if request.method == "DELETE":
            if Follow.objects.filter(user=request.user, author=author).exists():
                Follow.objects.filter(user=request.user, author=author).delete()
                return Response("Подписка удалена", status=status.HTTP_200_OK)
            return Response(
                {"detail": "Вы и не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST)
            
class MySubscriptionViewSet(viewsets.ModelViewSet):
    queryset =  User.objects.all()
    serializer_class = MySubcriptionsSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(following__user = request.user)
        return Response(MySubcriptionsSerializer(queryset, many = True).data, status=status.HTTP_200_OK)