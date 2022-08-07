from colorfield.fields import ColorField
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

    ingredient = models.ManyToManyField(Ingredient, through="IngredientRecipeAmount")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    tag = models.ManyToManyField(Tag, through="TagRecipe")
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="media/",
    )
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=2000)
    cooking_time = models.IntegerField()

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
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.ingredient} {self.recipe} {self.amount}"


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

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


class Favorites(models.Model):

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


class Shopping_cart(models.Model):

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
