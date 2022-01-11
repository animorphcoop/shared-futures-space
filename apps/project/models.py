# pyre-strict

from django.db import models
from userauth.models import CustomUser # pyre-ignore[21]

class Idea(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    proposed = models.ForeignKey('userauth.CustomUser', null=True, on_delete=models.SET_NULL) # null=true means nullable

class IdeaSupport(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)

# ---

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)

class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    owner = models.BooleanField(default = False)

class ProjectSupport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
