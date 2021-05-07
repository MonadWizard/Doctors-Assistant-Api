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
    sex = models.CharField(max_length=3, choices=CHOICES, default="M")
    phone = models.CharField(max_length=25, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    diagnosis = models.CharField(max_length=200, blank=True)
    prof_surgeon_consultant = models.CharField(max_length=200, blank=True)
    date_of_admission = models.DateTimeField(auto_now_add=True)
    date_of_discharge = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class PatientInfos(models.Model):
    # Info Types
    CHOICES = (
        ('L', 'Lab'),
        ('S', 'Surgery'),
        ('O', 'Other'),
    )

    type = models.CharField(max_length=3, choices=CHOICES, default="L")
    referred_by = models.CharField(max_length=50, blank=True)
    specimen = models.CharField(max_length=150, blank=True)
    investigation = models.CharField(max_length=250, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    finishing_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = "PatientInfos"

    def __str__(self):
        return self.type


class Assign(models.Model):
    """
    Assign Lab or Surgery
    """

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    patient_info_id = models.ForeignKey(PatientInfos, on_delete=models.CASCADE)

    def __str__(self):
        return self.patient_info_id.type + " for " + self.patient_id.name


class MediaImage(models.Model):
    patient_info_id_from_assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')


class MediaVideo(models.Model):
    patient_info_id_from_assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    video = models.FileField(upload_to='video/%Y/%m/%d/')


class MediaDocument(models.Model):
    patient_info_id_from_assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    document = models.FileField(upload_to='document/%Y/%m/%d/')
