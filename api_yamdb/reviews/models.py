from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название категории")
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name="Слаг категории")

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название жанра")
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name="Слаг жанра")

    class Meta:
        ordering = ("name",)
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    year = models.PositiveSmallIntegerField()
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="titles",
        db_column="genre",
        verbose_name="Жанр",
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name="categories",
        db_column="category",
        verbose_name="Категория",
        db_index=True,
    )
    description = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="reviews", verbose_name="Автор"
    )
    pub_date = models.DateTimeField("Дата отзыва", auto_now_add=True)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Объект",
        db_index=True,
    )
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name="Оценка"
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="rating_once")
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор"
    )
    pub_date = models.DateTimeField("Дата добавления",
                                    auto_now_add=True, db_index=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=f"{User.first_name} автора комментария",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text
