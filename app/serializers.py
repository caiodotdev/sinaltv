from rest_framework import serializers


from app.models import Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


from app.models import Channel
class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("id", "title", "code", "image", "url", "category", "program_url")


