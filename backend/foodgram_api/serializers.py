from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.models import (Favorites, Follow, Ingredient,
                             IngredientRecipeAmount, Recipe, Shopping_cart,
                             Tag)
from users.models import User

# from users.serializers import CustomUserSerializer



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
    ingredient = IngredientsEditSerializer(
        source="ingredientrecipeamount_set", many=True
    )
    author = CustomUserListSerializer(read_only=True)
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredient",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "tag",
            "name",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        tag = validated_data.pop("tag")
        ingredients_data = validated_data.pop("ingredientrecipeamount_set")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.set(tag)
        for ingredients in ingredients_data:
            IngredientRecipeAmount.objects.create(recipe=recipe, **ingredients)
        return recipe

    def to_representation(self, instance):
        """меняем формат списка айди тегов на список словарей со всеми данными тегов"""
        rep = super().to_representation(instance)
        tag_list = []
        for tag in rep["tag"]:
            tag = get_object_or_404(Tag, id=tag)
            single_tag = TagSerializer(tag).data
            tag_list.append(single_tag)
        rep["tag"] = tag_list
        return rep

    def update(self, instance, validated_data):

        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tag.clear()
        tag = validated_data.pop("tag")
        instance.tag.set(tag)
        IngredientRecipeAmount.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop("ingredientrecipeamount_set")
        for ingredients in ingredients_data:
            IngredientRecipeAmount.objects.create(recipe=instance, **ingredients)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Shopping_cart.objects.filter(user=request.user, recipe=obj).exists()


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
        print("obj", obj)
        queryset = Recipe.objects.filter(author = obj)
        return RecipeShortSerializer(queryset, many = True).data

class MySubcriptionsSerializer(serializers.ModelSerializer):
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
        return True

    def get_recipies_count(self, obj):
        return Recipe.objects.filter(author = obj).count()