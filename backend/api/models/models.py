from django.db import models
from django.contrib.auth.models import User

# custom user profile model to show user details integrating user info with fbid
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firebase_uid = models.CharField(max_length=128, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.email} ({self.firebase_uid}) - {self.role}"

# The __str__() method controls how the object appears when you print it or view it in places like:

# child model
# note: child must be created with concerns (many - many)
class Child(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    therapistMatches = models.ManyToManyField('TherapistMatch', related_name='children', blank=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    birthDate = models.DateField()
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    concerns = models.ManyToManyField('Concern', related_name='children', blank=True)
    def __str__(self):
        return self.name
    
    # therapist model
class Therapist(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='therapist_images/')
    expertise = models.ManyToManyField('Expertise', related_name='therapists')
    experience_years = models.IntegerField()
    bio = models.TextField()
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name