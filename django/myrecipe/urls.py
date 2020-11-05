from rest_framework import routers
from django.contrib import admin
from django.urls import path, include

from .apps.recipe import views


router = routers.DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("recipe-ingredients", views.RecipeIngredientViewSet)
router.register("users", views.UserViewSet)

urlpatterns = [
    path("backend/admin/", admin.site.urls),
    path("backend/accounts/", include("allauth.urls")),
    path("backend/", include(router.urls)),
]
