from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from .apps.recipe import views


router = routers.DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("recipe-ingredients", views.RecipeIngredientViewSet)
router.register("users", views.UserViewSet)
router.register("view-permissions", views.ViewPermissionViewSet)

urlpatterns = [
    path("backend/admin/", admin.site.urls),
    path("backend/accounts/", include("allauth.urls")),
    path("backend/test/", TemplateView.as_view(template_name="index.html")),
    path("backend/", include(router.urls)),
]
