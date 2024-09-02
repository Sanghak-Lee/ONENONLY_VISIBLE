from django.urls import path, include
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter
from . import views

app_name = "artist"
router = DefaultRouter()

router.register("", views.ArtistViewSet)


urlpatterns = [
    path("", include(router.urls)),
]