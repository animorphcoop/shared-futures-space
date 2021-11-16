# pyre-strict

from django.db import models
from userauth.models import CustomUser # pyre-ignore[21]

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)

class ProjectOwnership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class ProjectSupport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    message = models.CharField(max_length=2000)
    user_from = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
