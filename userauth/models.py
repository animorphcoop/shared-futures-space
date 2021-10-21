from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse


class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    display_name = models.CharField(verbose_name=_("Display name"),
                                    max_length=30, help_text=_("Will be shown alongside entries"), null=True)
    year_of_birth = models.PositiveIntegerField(verbose_name=_("Year of birth"),
                                                validators=[MinValueValidator(1900), MaxValueValidator(2021)],
                                                null=True)
    post_code = models.CharField(verbose_name=_("Post code"), max_length=8, null=True)

    class Meta:
        ordering = ['display_name']

    # to redirect to account profile page
    def get_absolute_url(self):
        return reverse('profile')

    def __str__(self):
        return f"{self.display_name}"
