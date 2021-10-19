from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUser(AbstractUser):
    display_name = models.CharField(verbose_name=_("Display name"),
                                    max_length=30, help_text=_("Will be shown alongside entries"))
    year_of_birth = models.PositiveIntegerField(verbose_name=_("Year of birth"),
                                                validators=[MinValueValidator(1900), MaxValueValidator(2021)])
    post_code = models.CharField(verbose_name=_("Post code"), max_length=8)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return f"{self.display_name}: {self.first_name} {self.last_name}"
