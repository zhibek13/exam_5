from django.db import IntegrityError
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from .models import News, Comment, Status, NewsStatus, CommentStatus
from .serializers import NewsSerializer, CommentSerializer, StatusSerializer
from .permissions import IsAuthorPermission, IsStaffPermission
from account.models import Author
from django.shortcuts import render


class NewsCreateListView(ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.author)


class NewsRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


class CommentListCreateView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthorPermission,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.author, news=News.objects.get(id=self.kwargs["news_id"]))

    def get_queryset(self):
        return self.queryset.filter(news=self.kwargs['news_id'])


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


class StatusListCreateView(ListCreateAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsStaffPermission, )


class StatusRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsStaffPermission, )


class NewsStatusGET(APIView):
    permission_classes = (IsAuthorPermission, )

    def get(self, request, news_id, status_slug):
        news = get_object_or_404(News, id=news_id)
        news_status = get_object_or_404(Status, slug=status_slug)
        try:
            stat_add = NewsStatus.objects.create(news=news, author=request.user.author, status=news_status)
            save_status = status.HTTP_200_OK
        except IntegrityError:
            stat_add = NewsStatus.objects.get(news=news, author=request.user.author,)
            data = {'message': f'You already added status'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f'Status added'}
            return Response(data, status=status.HTTP_201_CREATED)


class CommentsStatusGET(APIView):
    permission_classes = (IsAuthorPermission, )

    def get(self, request, news_id, comment_id, status_slug):
        comment = get_object_or_404(Comment, id=comment_id)
        comment_status = get_object_or_404(Status, slug=status_slug)
        try:
            stat_add = CommentStatus.objects.create(comment=comment, author=request.user.author, status=comment_status)
            save_status = status.HTTP_200_OK
        except IntegrityError:
            stat_add = CommentStatus.objects.get(comment=comment, author=request.user.author,)
            data = {'message': f'You already added status'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f'Status added'}
            return Response(data, status=status.HTTP_201_CREATED)
