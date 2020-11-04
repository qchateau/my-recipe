from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from . import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = serializers.UserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        return Response(self.get_serializer((request.user)).data)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="give-permission",
    )
    def give_permission(self, request):
        user_from = request.user
        user_to = self.get_queryset().get(email=request.data["email"])
        models.ViewPermission.objects.get_or_create(
            user_from=user_from, user_to=user_to
        )
        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="revoke-permission",
    )
    def revoke_permission(self, request):
        user_from = request.user
        user_to = self.get_queryset().get(email=request.data["email"])
        models.ViewPermission.objects.get(user_from=user_from, user_to=user_to).delete()
        return Response()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all().order_by("id")
    serializer_class = serializers.RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        self._verify_is_author()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._verify_is_author()
        return super().perform_destroy(instance)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_superuser:
            allowed_authors = [user] + list(
                User.objects.filter(view_permissions__user_to=user)
            )
            queryset = queryset.filter(author__in=allowed_authors)

        name_search = self.request.query_params.get("name-search", None)
        if name_search is not None:
            queryset = queryset.filter(name__icontains=name_search)
        return queryset

    def _verify_is_author(self):
        user = self.request.user
        if user.is_superuser:
            return

        if self.get_object().author != user:
            self.permission_denied(
                self.request,
                message="You do not have permission to perform this action.",
                code=403,
            )


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = models.RecipeIngredient.objects.all().order_by("id")
    serializer_class = serializers.RecipeIngredientSerializer


class ViewPermissionViewSet(viewsets.ModelViewSet):
    queryset = models.ViewPermission.objects.all().order_by("id")
    serializer_class = serializers.ViewPermissionSerializer
