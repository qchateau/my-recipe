from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from . import models

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class RecipeIngredientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.RecipeIngredient
        fields = ["id", "name", "quantity", "unit"]


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
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
        ingredients = validated_data.pop("ingredients", None)
        with transaction.atomic():
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()

            # ingredients is None only in the case of a patch which does not include it
            if ingredients is not None:
                instance.ingredients.all().delete()
                for ingredient in ingredients:
                    models.RecipeIngredient.objects.create(
                        recipe=instance, **ingredient
                    )

        return instance
