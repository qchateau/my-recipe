from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Recipe, RecipeIngredient


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "quantity", "unit"]


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, default=list)

    class Meta:
        model = Recipe
        fields = "__all__"

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        instance.ingredients.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=instance, **ingredient)
        return instance
