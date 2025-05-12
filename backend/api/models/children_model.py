from django.db import models

class Concern(models.Model):
    title = models.CharField(max_length=100, unique=True) 
    description = models.TextField() 

    def __str__(self):
        return self.title

class Language(models.Model):
    languages = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.languages
