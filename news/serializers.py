from rest_framework import serializers

from .models import News, Comment, Status


class NewsSerializer(serializers.ModelSerializer):
    get_status = serializers.ReadOnlyField()

    class Meta:
        model = News
        fields = "__all__"
        read_only_fields = ("author",)


class CommentSerializer(serializers.ModelSerializer):
    get_status = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("author", "news")


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"
