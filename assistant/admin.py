from django.contrib import admin

from .models import (
    Patient,
    PatientInfos,
    MediaVideo,
    MediaImage,
    MediaDocument,
    Assign
)

from django import forms


class PatientAdminForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = "__all__"


class PatientAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = [
        "diagnosis",
        "date_of_discharge",
        "phone",
        "date_of_admission",
        "age",
        "address",
        "prof_surgeon_consultant",
        "name",
        "sex",
    ]
    readonly_fields = [
        "date_of_admission",
    ]


admin.site.register(Patient, PatientAdmin)


class PatientInfosAdminForm(forms.ModelForm):
    class Meta:
        model = PatientInfos
        fields = "__all__"


class PatientInfosAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = '__all__'
    readonly_fields = [

    ]


admin.site.register(PatientInfos, PatientInfosAdmin)

admin.site.register(Assign)
admin.site.register(MediaVideo)
admin.site.register(MediaImage)
admin.site.register(MediaDocument)
