from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from foodgram.models import (Favorite, Follow, Ingredient,
                             IngredientRecipeAmount, Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User


class CustomUserListSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("username", "email", "last_name", "first_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author = obj).exists()
    

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id",)


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.StringRelatedField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientRecipeAmount
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeShortSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only = True)
    name = serializers.StringRelatedField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsEditSerializer(
        source="ingredientrecipeamount_set", many=True
    )
    author = CustomUserListSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "tags",
            "name",
            "text",
            "cooking_time",
        )

    def create_ingredients(self, ingredients_data , recipe):
        new_ingredients = [
            IngredientRecipeAmount(
                recipe=recipe,
                ingredient = ingredient_data['ingredient'],
                amount = ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data 
        ]
        IngredientRecipeAmount.objects.bulk_create(new_ingredients)
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredientrecipeamount_set")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def to_representation(self, instance):
        """меняем формат списка айди тегов на список словарей со всеми данными тегов"""
        rep = super().to_representation(instance)
        tags_set = Tag.objects.filter(id__in = rep["tags"])
        rep["tags"] = TagSerializer(tags_set, many = True).data
        return rep

    def update(self, instance, validated_data):

        instance.tags.clear()
        tags = validated_data.pop("tags")
        instance.tags.set(tags)
        IngredientRecipeAmount.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop("ingredientrecipeamount_set")
        self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()


class SubcriptionsSerializer(serializers.ModelSerializer):
    recipies = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "last_name",
            "first_name",
            "recipies",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author = obj).exists()

    def get_recipies(self, obj):
        queryset = Recipe.objects.filter(author = obj)
        return RecipeShortSerializer(queryset, many = True).data

class SubcriptionsListSerializer(serializers.ModelSerializer):
    recipies = serializers.SerializerMethodField()
    recipies_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "last_name",
            "first_name",
            "recipies",
            "is_subscribed",
            "recipies_count"
        )
    
    def get_recipies(self, obj):
        queryset = Recipe.objects.filter(author = obj)
        return RecipeShortSerializer(queryset, many = True).data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipies_count(self, obj):
        return Recipe.objects.filter(author = obj).count()