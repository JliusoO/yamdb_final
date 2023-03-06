from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    CreateUserAPIView,
    GetTokenAPIView,
)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register("users", UserViewSet, basename="users")
v1_router.register("titles", TitleViewSet, basename="title")
v1_router.register("categories", CategoryViewSet,
                   basename="category")
v1_router.register("genres", GenreViewSet, basename="genre")
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="review"
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comment",
)

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/signup/", CreateUserAPIView.as_view(), name="signup"),
    path("v1/auth/token/", GetTokenAPIView.as_view(), name="login"),
]
