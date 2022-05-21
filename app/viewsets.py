from rest_framework import viewsets

from django_filters import rest_framework as filters

from . import (
    serializers,
    models
)

import django_filters



class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = models.Category
        fields = ["id", "name"]


class CategoryViewSet(viewsets.ModelViewSet):
    
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter



class ChannelFilter(django_filters.FilterSet):
    class Meta:
        model = models.Channel
        fields = ["id", "title", "code", "image", "url", "category__name", "program_url"]


class ChannelViewSet(viewsets.ModelViewSet):
    
    serializer_class = serializers.ChannelSerializer
    queryset = models.Channel.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ChannelFilter

