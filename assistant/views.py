from rest_framework import viewsets, permissions
from account.permissions import IsDoctor
from . import serializers
from . import models


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for the Patient class"""

    queryset = models.Patient.objects.all()
    serializer_class = serializers.PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]


class PatientInfosViewSet(viewsets.ModelViewSet):
    """ViewSet for the PatientInfos class"""

    queryset = models.PatientInfos.objects.all()
    serializer_class = serializers.PatientInfosSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]


class MediaImageViewSet(viewsets.ModelViewSet):
    """ViewSet for the MediaImage class"""

    queryset = models.MediaImage.objects.all()
    serializer_class = serializers.MediaImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]


class MediaVideoViewSet(viewsets.ModelViewSet):
    """ViewSet for the MediaVideo class"""

    queryset = models.MediaVideo.objects.all()
    serializer_class = serializers.MediaVideoSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]


class MediaDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for the MediaDocument class"""

    queryset = models.MediaDocument.objects.all()
    serializer_class = serializers.MediaDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]


class AssignViewSet(viewsets.ModelViewSet):
    """ViewSet for the Assign class"""

    queryset = models.Assign.objects.all()
    serializer_class = serializers.AssignSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
