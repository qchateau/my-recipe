from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Recipe, RecipeIngredient
from .serializers import RecipeSerializer, RecipeIngredientSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        return Response(self.get_serializer((request.user)).data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        name_search = self.request.query_params.get("name-search", None)
        if name_search is not None:
            queryset = queryset.filter(name__icontains=name_search)
        return queryset


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
