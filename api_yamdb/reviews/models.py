# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.db import models
#
# from users.models import User
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=256, verbose_name="Название категории")
#     slug = models.SlugField(unique=True, max_length=50,
#                             verbose_name="Слаг категории")
#
#     class Meta:
#         ordering = ("name",)
#         verbose_name = "Категория"
#         verbose_name_plural = "Категории"
#
#     def __str__(self):
#         return self.name
#
#
# class Genre(models.Model):
#     name = models.CharField(max_length=256, verbose_name="Название жанра")
#     slug = models.SlugField(unique=True, max_length=50,
#                             verbose_name="Слаг жанра")
#
#     class Meta:
#         ordering = ("name",)
#         verbose_name = "Жанр"
#         verbose_name_plural = "Жанры"
#
#     def __str__(self):
#         return self.name
#
#
# class Title(models.Model):
#     name = models.CharField(max_length=256, db_index=True)
#     year = models.PositiveSmallIntegerField()
#     genre = models.ManyToManyField(
#         Genre,
#         blank=True,
#         related_name="titles",
#         db_column="genre",
#         verbose_name="Жанр",
#         db_index=True,
#     )
#     category = models.ForeignKey(
#         Category,
#         blank=True,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="categories",
#         db_column="category",
#         verbose_name="Категория",
#         db_index=True,
#     )
#     description = models.TextField(max_length=500, blank=True)
#
#     class Meta:
#         ordering = ("name",)
#         verbose_name = "Произведение"
#         verbose_name_plural = "Произведения"
#
#     def __str__(self):
#         return self.name
#
#
# class Review(models.Model):
#     text = models.TextField(verbose_name="Текст отзыва")
#     author = models.ForeignKey(
#         User, on_delete=models.CASCADE,
#         related_name="reviews", verbose_name="Автор"
#     )
#     pub_date = models.DateTimeField("Дата отзыва", auto_now_add=True)
#     title = models.ForeignKey(
#         Title,
#         on_delete=models.CASCADE,
#         related_name="reviews",
#         verbose_name="Объект",
#         db_index=True,
#     )
#     score = models.PositiveSmallIntegerField(
#         validators=[MaxValueValidator(10), MinValueValidator(1)],
#         verbose_name="Оценка"
#     )
#
#     class Meta:
#         ordering = ["-pub_date"]
#         verbose_name = "Отзыв"
#         verbose_name_plural = "Отзывы"
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["author", "title"], name="rating_once")
#         ]
#
#     def __str__(self):
#         return self.text
#
#
# class Comment(models.Model):
#     text = models.TextField(verbose_name="Текст комментария")
#     author = models.ForeignKey(
#         User, on_delete=models.CASCADE,
#         related_name="comments", verbose_name="Автор"
#     )
#     pub_date = models.DateTimeField("Дата добавления",
#                                     auto_now_add=True, db_index=True)
#     review = models.ForeignKey(
#         Review,
#         on_delete=models.CASCADE,
#         related_name="comments",
#         verbose_name=f"{User.first_name} автора комментария",
#     )
#
#     class Meta:
#         verbose_name = "Комментарий"
#         verbose_name_plural = "Комментарии"
#
#     def __str__(self):
#         return self.text
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import validate_username, validate_year

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='XXXX'
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()


class Category(models.Model):
    name = models.CharField(
        'имя категории',
        max_length=200
    )
    slug = models.SlugField(
        'слаг категории',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} {self.name}'


class Genre(models.Model):
    name = models.CharField(
        'имя жанра',
        max_length=200
    )
    slug = models.SlugField(
        'cлаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return f'{self.name} {self.name}'


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
        db_index=True
    )
    year = models.IntegerField(
        'год',
        validators=(validate_year, )
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        'описание',
        max_length=255,
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.CharField(
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    score = models.IntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )
    text = models.CharField(
        'текст комментария',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
