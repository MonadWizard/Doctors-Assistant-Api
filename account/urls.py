from django.urls import path, include
from .views import (
    DoctorRegisterPhone,
    UserViewSet,
    PhoneValidateView,
    OtpValidateView,
    DoctorRegisterEmail,
    ProfileActivate,
    CustomTokenObtainPairView,
    UserVerificationView,
    DoctorProfileView,
    EmailUpdateView,
    EmailVerify,
    UserVerify,
    PhoneUpdateView,
    PasswordUpdateView,
    DoctorListView,
    AddressListView
)

from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Doctors Assistant API')

router = routers.DefaultRouter()
# user-list
router.register('list', UserViewSet)
# router.register('doctor/list', DoctorListView)


router.register('doctor/profile', DoctorProfileView)
router.register('email', EmailUpdateView)  # view to update email
router.register('phone', PhoneUpdateView)  # view to update phone'
# router.register('password', PasswordUpdateView)  # view to update phone

urlpatterns = [
    path('', schema_view),

    # registration by phone url
    path('user/phone-validate', PhoneValidateView.as_view(), name='phone-validate'),
    path('user/otp-validate', OtpValidateView.as_view(), name='otp-validate'),
    path('user/register/doctor', DoctorRegisterPhone.as_view()),

    # registration by email url
    path('user/register/doctor/email', DoctorRegisterEmail.as_view()),

    path('activate/<slug:uidb64>/<slug:token>/', ProfileActivate.as_view(), name="activate"),  # activates the account

    # login
    # path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('verification/', UserVerificationView.as_view(), name='verification'),

    # account verify for sensitive information update

    path('user/verify', UserVerify.as_view(), name='user-verifies'),  # verifies user for sensitive information update
    path('verify/<slug:uidb64>/<slug:token>/', EmailVerify.as_view(),
         name="user-verify"),  # verifies email id and updates

    path('user/password/update', PasswordUpdateView.as_view(), name='password-update'),

    # list
    path('user/doctor/list', DoctorListView.as_view(), name='doctor-list'),

    path('address/list', AddressListView.as_view(), name='address-list'),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('user/', include(router.urls)),
]
