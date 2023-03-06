from django.conf import settings
from django.db.models import Avg
from django.core.management.utils import get_random_secret_key
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import (
    ConfirmationCodeSerializer,
    EmailSerializer,
    UserSerializer,
    CommentSerializer,
    ReviewsSerializer,
    TitleCreateUpdateSerializer,
    TitleSerializer,
    GenreSerializer,
    CategorySerializer,
)
from reviews.models import Category, Genre, Review, Title
from users.models import User
from .permissions import (
    IsAuthorAdminModeratorOrReadOnly, IsAdmin, IsAdminOrReadOnly)
from .filters import TitleFilter


class CreateUserAPIView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get("email")
        username = request.data.get("username")
        confirmation_code = get_random_secret_key()
        User.objects.create(
            email=email, username=username, confirmation_code=confirmation_code
        )
        title = "Пришел код подтверждения"
        message = f"Ваш код подтверждения - {confirmation_code}"
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"email": email, "username": username}, status=status.HTTP_200_OK
        )


class GetTokenAPIView(APIView):
    def post(self, request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)

        if user.confirmation_code == request.data.get("confirmation_code"):
            return Response(
                f"Твой токен - {AccessToken.for_user(user)}",
                status=status.HTTP_200_OK
            )
        return Response(
            "Код подтверждения не корректен",
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["pk"])

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        name="get_patch_user",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def review(self):
        return get_object_or_404(Review, pk=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.review())


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title())


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "slug"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["=name"]


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "slug"
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ["=name"]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().annotate(
            rating=Avg("reviews__score")).order_by("name")
    )
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TitleFilter
    ordering_fields = ("name",)

    def get_serializer_class(self):
        if self.action == "create" or self.action == "partial_update":
            return TitleCreateUpdateSerializer
        return TitleSerializer
