from rest_framework.routers import DefaultRouter
from app import (
    viewsets
)

api_urlpatterns = []

category_router = DefaultRouter()

category_router.register(
    r'^api/category',
    viewsets.CategoryViewSet,
    basename="category"
)

api_urlpatterns += category_router.urls
channel_router = DefaultRouter()

channel_router.register(
    r'^api/channel',
    viewsets.ChannelViewSet,
    basename="channel"
)

api_urlpatterns += channel_router.urls
