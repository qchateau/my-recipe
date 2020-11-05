from rest_framework import serializers
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "url", "username", "first_name", "last_name", "email"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.RecipeIngredient
        fields = ["id", "name", "quantity", "unit"]


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, default=list)

    class Meta:
        model = models.Recipe
        fields = "__all__"

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = models.Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            models.RecipeIngredient.objects.create(recipe=recipe, **ingredient)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        instance.ingredients.all().delete()
        for ingredient in ingredients:
            models.RecipeIngredient.objects.create(recipe=instance, **ingredient)
        return instance
