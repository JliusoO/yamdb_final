from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    ROLE = [
        (ADMIN, "админ"),
        (USER, "пользователь"),
        (MODERATOR, "модератор"),
    ]

    email = models.EmailField(max_length=100, unique=True,
                              verbose_name="email")
    first_name = models.CharField(max_length=150, blank=True,
                                  verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True,
                                 verbose_name="Фамилия")
    confirmation_code = models.CharField(
        max_length=155, blank=True, null=True, verbose_name="Код подтверждения"
    )
    bio = models.TextField(verbose_name="Биография", blank=True)
    role = models.CharField(max_length=55, choices=ROLE, default=USER)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_together"
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
