from rest_framework import serializers

from . import models


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Patient
        fields = [
            "name",
            "diagnosis",
            "sex",
            "age",
            "phone",
            "address",
            "prof_surgeon_consultant",
            "date_of_discharge",
            "date_of_admission",
        ]


class PatientInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PatientInfos
        fields = '__all__'


class MediaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MediaImage
        fields = '__all__'


class MediaVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MediaVideo
        fields = '__all__'


class MediaDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MediaDocument
        fields = '__all__'


class AssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assign
        fields = '__all__'
