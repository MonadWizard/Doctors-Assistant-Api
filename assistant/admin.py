from django.contrib import admin

# Register your models here.
from .models import Patient, PatientInfos, Media, MediaVideo, MediaImage, MediaDocument, Assign

admin.site.register(Patient)
admin.site.register(PatientInfos)
admin.site.register(Assign)
admin.site.register(Media)
admin.site.register(MediaVideo)
admin.site.register(MediaImage)
admin.site.register(MediaDocument)