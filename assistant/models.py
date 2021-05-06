from django.db import models


# Create your models here.


class Patient(models.Model):
    # Gander Choices
    CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    name = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    sex = models.CharField(max_length=3, choices=CHOICES, default=CHOICES.index(1))
    phone = models.CharField(max_length=25, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    diagnosis = models.CharField(max_length=200, blank=True)
    prof_surgeon_consultant = models.CharField(max_length=200, blank=True)
    date_of_admission = models.DateTimeField(auto_now_add=True)
    date_of_discharge = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class MediaImage(models.Model):
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')


class MediaVideo(models.Model):
    video = models.FileField(upload_to='video/%Y/%m/%d/')


class MediaDocument(models.Model):
    video = models.FileField(upload_to='document/%Y/%m/%d/')


class Media(models.Model):
    pass