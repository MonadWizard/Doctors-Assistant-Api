from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PatientViewSet,
    PatientInfosViewSet,
    MediaImageViewSet,
    MediaVideoViewSet,
    MediaDocumentViewSet,
    AssignViewSet
)

router = DefaultRouter()
router.register('patient', PatientViewSet)  # for patient - post and get
router.register('info', PatientInfosViewSet)  # for patient - post and get
router.register('assign', AssignViewSet)  # for patient - post and get
router.register('image', MediaImageViewSet)  # for patient - post and get
router.register('video', MediaVideoViewSet)  # for patient - post and get
router.register('document', MediaDocumentViewSet)  # for patient - post and get

urlpatterns = [
    path('api/', include(router.urls)),
]
