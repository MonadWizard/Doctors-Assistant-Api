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
        "name",
        "diagnosis",
        "sex",
        "phone",
        "age",
        "assign_doctor",
        "date_of_admission",
        "date_of_discharge",
        "address",
        "prof_surgeon_consultant",
    ]
    readonly_fields = [
        "date_of_admission",

    ]
    search_fields = [
        'name',
        'phone',
        'diagnosis',
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'assign_doctor', None) is None:
            obj.author = request.user
        obj.save()


admin.site.register(Patient, PatientAdmin)


class PatientInfosAdminForm(forms.ModelForm):
    class Meta:
        model = PatientInfos
        fields = "__all__"


class PatientInfosAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = [
        'type',
        'referred_by',
        'specimen',
        'investigation',
        'created_date',
        'finishing_date',
    ]
    readonly_fields = [
        'created_date',

    ]


admin.site.register(PatientInfos, PatientInfosAdmin)

admin.site.register(Assign)
admin.site.register(MediaVideo)
admin.site.register(MediaImage)
admin.site.register(MediaDocument)
