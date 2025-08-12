from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя с дополнительными полями."""

    email = models.EmailField(
        'Email', unique=True,
        max_length=254, db_index=True
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    avatar = models.ImageField(
        'Аватар', upload_to='users/',
        null=True, blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Подписка на автора."""

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='на себя подписаться низя'
            )
        ]
        ordering = ['user']

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
