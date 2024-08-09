from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

from users.models import JostarUser


class BaseJostarModel(models.Model):
    is_deleted = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Jostar(BaseJostarModel):
    author = models.ForeignKey(
        JostarUser,
        on_delete=models.CASCADE,
        related_name='jostars'
    )
    title = models.CharField(max_length=25, null=False)
    content = models.TextField()
    number_of_ratings = models.PositiveIntegerField(null=False, default=0)
    average_rating = models.FloatField(null=False, default=0)


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    jostar = models.ForeignKey(
        Jostar,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        null=False,
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'jostar')
