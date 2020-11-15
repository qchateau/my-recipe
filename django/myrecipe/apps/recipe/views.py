from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from . import models, serializers

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = serializers.UserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        return Response(self.get_serializer((request.user)).data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all().order_by("name")
    serializer_class = serializers.RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *_, **__):
        user = self.request.user

        queryset = self.get_queryset()
        if not user.is_superuser:
            queryset = queryset.filter(author=user)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        user_is_author = request.user.is_superuser or obj.author == request.user

        if (not user_is_author) and (
            request.method not in permissions.SAFE_METHODS or not obj.public
        ):
            self.permission_denied(
                self.request,
                message="You do not have permission to perform this action.",
                code=403,
            )

    def get_queryset(self):
        queryset = super().get_queryset()

        name_search = self.request.query_params.get("name-search", None)
        if name_search is not None:
            queryset = queryset.filter(name__icontains=name_search)
        return queryset


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = models.RecipeIngredient.objects.all().order_by("id")
    serializer_class = serializers.RecipeIngredientSerializer
