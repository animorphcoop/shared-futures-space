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

# no IdeaMessage because we're going to have a proper messaging system to roll that stuff into

# ---

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)

class ProjectOwnership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)

class ProjectSupport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)

class ProjectMessage(models.Model): # a message sent to the owners of a project, eg "I'll support this if ..."
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    message = models.CharField(max_length=2000)
    user_from = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
