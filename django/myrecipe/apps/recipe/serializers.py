from rest_framework import serializers
from django.contrib.auth.models import User

from . import models


class ViewPermissionUserToEmailSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.user_to.email


class UserSerializer(serializers.ModelSerializer):
    view_permissions = ViewPermissionUserToEmailSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "url",
            "username",
            "first_name",
            "last_name",
            "email",
            "view_permissions",
        ]


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


class ViewPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ViewPermission
        fields = "__all__"
