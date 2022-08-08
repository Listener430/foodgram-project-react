from colorfield.fields import ColorField
from django.core import validators
from django.db import models
from users.models import User


class Ingredient(models.Model):

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиент"


class Tag(models.Model):

    name = models.CharField(max_length=200, unique=True)
    color = ColorField(default="#FF0000", unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Таг"
        verbose_name_plural = "Теги"


class Recipe(models.Model):

    ingredients = models.ManyToManyField(Ingredient, through="IngredientRecipeAmount")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    tags = models.ManyToManyField(Tag, through="TagRecipe")
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="media/",
    )
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=2000)
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
        validators=(
            validators.MinValueValidator(
                1, message="больше 1"),
        ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):

        return self.name


class IngredientRecipeAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredientrecipeamount"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество ингредиентов")

    class Meta:
        verbose_name = "Количество ингридиента"
        verbose_name_plural = "Количество ингридиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredients_recipe"
            )
        ]
    def __str__(self):
        return f"{self.ingredient} {self.recipe} {self.amount}"


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tag", "recipe"],
                name="unique_tag_recipe")
        ]

        verbose_name = "Тег"
        verbose_name_plural = "Теги на рецепты"
    def __str__(self):
        return f"{self.tag} {self.recipe}"


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="follower",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"], name="unique_follower")
        ]


class Favorite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="recipe_follower",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="following_recipe",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_follower")
        ]


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="shopping_cart_follower",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_following_recipe",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_follower")
        ]
