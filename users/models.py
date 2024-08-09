from django.contrib.auth.models import AbstractUser
from django.db import models


class JostarUser(AbstractUser):
    # Added this model just in case I need to add
    # more fields to my user entity
    pass
