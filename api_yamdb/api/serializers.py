from rest_framework import serializers
from django.utils import timezone

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField()
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ("id", "rating", "name", "year",
                  "description", "genre", "category")
        read_only_fields = ("__all__",)


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year",
                  "description", "genre", "category")

    def validate_year(self, value):
        year = timezone.datetime.now().year
        if value > year:
            raise serializers.ValidationError(
                f"Год выпуска не больше {year}")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def validate(self, data):
        title = self.context.get("view").kwargs.get("title_id")
        author = self.context.get("request").user
        if (
            self.context.get("request").method == "POST"
            and Review.objects.filter(author=author, title=title).exists()
        ):
            raise serializers.ValidationError(
                "Вы уже оставляли отзыв на это произведение!"
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name",
                  "email", "bio", "role"]


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username"]

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError("Недопустимое имя пользователя")
        return value


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
