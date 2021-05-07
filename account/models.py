from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save


class User(AbstractUser):
    # type of users
    admin = models.BooleanField(default=False)
    doctors = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)

    username = models.CharField(max_length=255, unique=True)  # email or phone
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=255, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return "{}".format(self.username + "-" + str(self.pk))

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        if self.phone == '':
            self.phone = None
        super().save(*args, **kwargs)


class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.user:
            return "{}".format((self.user.username) + "-" + str(self.pk))
        else:
            return "parcel address - " + str(self.pk)


class PhoneOtp(models.Model):
    """Object will be invalid if count>10"""
    phone = models.CharField(max_length=20)
    otp = models.CharField(max_length=10, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of OTP sent')
    created_at = models.DateTimeField(auto_now_add=True)
    validated = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format((self.phone) + "-" + str(self.otp))


class DoctorsProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    # address will be added to UserAddress table using signal
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='doctor_address')

    image = models.ImageField(upload_to='doctors/file_folder/', null=True, blank=True)

    org_name = models.CharField(max_length=100, blank=True, null=True)
    org_type = models.CharField(max_length=100, blank=True, null=True)  # can be choice

    nid_no = models.CharField(max_length=100, blank=True, null=True)
    doctors_id = models.CharField(max_length=100, blank=True, null=True)

    # nid_image = models.ImageField(upload_to='seller/file_folder/', null=True, blank=True)

    def __str__(self):
        return "{}".format(self.user.username + "-" + str(self.pk))


def create_user_profile(sender, instance, created, *args, **kwargs):
    # if instance.is_staff or instance.admin:
    #     """Creates AdminProfile object"""
    #     AdminProfile.objects.get_or_create(user=instance)
    if created:
        UserAddress.objects.get_or_create(user=instance)
        if instance.seller:
            DoctorsProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)
