from rest_framework.routers import DefaultRouter

from phoneverify.views import YourCustomViewSet

default_router = DefaultRouter(trailing_slash=False)
default_router.register('phone', YourCustomViewSet, basename='phone')

urlpatterns = default_router.urls
