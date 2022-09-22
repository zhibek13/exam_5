from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# router = DefaultRouter()
# router.register('news', views.NewsViewSet, basename='news')

urlpatterns = [
    # path('', include(router.urls)),
    path('news/', views.NewsCreateListView.as_view(), name='news-create-list'),
    path('news/<int:pk>/', views.NewsRetrieveUpdateDestroyAPIView.as_view(), name='news-retrieve-update-destroy'),
    path('news/<int:news_id>/comments/', views.CommentListCreateView.as_view(), name='comment-create-list'),
    path('news/<int:news_id>/comments/<int:pk>/', views.CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-retrieve-update-destroy'),
    path('statuses/', views.StatusListCreateView.as_view(), name='status-create-list'),
    path('statuses/<int:pk>/', views.StatusRetrieveUpdateDestroyAPIView.as_view(), name='status-retrieve-update-destroy'),
    path('news/<int:news_id>/<str:status_slug>/', views.NewsStatusGET.as_view(), name='news-status-create-list'),
    path('news/<int:news_id>/comments/<int:comment_id>/<str:status_slug>/', views.NewsStatusGET.as_view(), name='comment-status-create-list'),
]
