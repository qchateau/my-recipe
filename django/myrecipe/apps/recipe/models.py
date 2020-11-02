from django.db import models
from django.conf import settings


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField()


class RecipeIngredient(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=100, default="", blank=True)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
