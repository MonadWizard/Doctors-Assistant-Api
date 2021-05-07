from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
import re
import random
from rest_framework import status
from six import text_type
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import datetime
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import generics

from .models import User, PhoneOtp, DoctorsProfile, UserAddress
from .serializer import (
    UserSerializer,
    DoctorRegisterSerializer,
    PhoneValidateSerializer,
    OtpValidateSerializer,
    DoctorEmailRegisterSerializer,
    CustomTokenObtainPairSerializer,
    VerificationSerializer,
    DoctorSerializer,
    EmailUpdateSerializer,
    PhoneUpdateSerializer,
    PasswordUpdateSerializer,
    DoctorListSerializer,
    UserAddressSerializer
)

User = get_user_model()


def home(request):
    return HttpResponse('Welcome to delivery management app')


class UserViewSet(viewsets.ModelViewSet):
    """ View for user list """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PhoneValidateView(APIView):
    """
    Upon receiving the phone number, checks if the number is valid. If valid, sends an OTP
    :parameter: phone
    """

    serializer_class = PhoneValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.data['phone']

        # checks if number is valid
        num_format = re.compile("^(?:\+?88)?01[13-9]\d{8}$")
        is_number = re.match(num_format, phone)
        if not is_number:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Please enter a valid phone number!"
            })

        # checks if number available
        if User.objects.filter(phone=phone).exists():
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "The Phone number is already taken. Please enter different number."
            })
        else:
            # generates key
            key = generate_otp(phone)
            if key:
                # checks if otp for this phone number already exists
                old = PhoneOtp.objects.filter(phone=phone).last()
                if old:
                    old.valid = False
                    old.save()

                phone_otp = PhoneOtp.objects.create(phone=phone, otp=key)
                phone_otp.save()

                # sends otp
                # send_otp(phone)

                return Response({
                    "status_code": status.HTTP_200_OK,
                    "phone": phone,
                    "otp": phone_otp.otp,
                    "message": "Otp is sent to you phone."
                })


class OtpValidateView(APIView):
    """
    Upon receiving the otp, checks if otp matches with phone.
    :parameter: phone, otp
    """
    serializer_class = OtpValidateSerializer

    def post(self, request, *args, **kwargs):
        """checks if otp matches with phone"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.data['phone']
        otp = serializer.data['otp']

        otp_obj = PhoneOtp.objects.filter(phone=phone, otp=otp, validated=False)
        if otp_obj.exists():
            # check expiry status, expiry_time = 5 minutes
            time = datetime.datetime.now(datetime.timezone.utc) - otp_obj.last().created_at
            if time < datetime.timedelta(minutes=5):
                otp_obj = otp_obj.last()
                otp_obj.validated = True
                otp_obj.save()
                return Response({
                    "status_code": status.HTTP_200_OK,
                    "message": "Otp matched.",
                })
            else:
                # otp_obj.last().save()
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Otp time has expired. Please resend otp."
                })
        else:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid otp"
            })


def generate_otp(phone):
    """
    View to Generate OTP
    """
    if phone:
        key = random.randint(999, 9999)
        return key
    else:
        return False


class DoctorRegisterPhone(APIView):
    """
    View to register Doctor using phone
    :parameter: phone, password, confirm_password, owner_name, org_name, org_type, image, address, nid_no, business_id
    """
    serializer_class = DoctorRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.data['password']
        c_password = serializer.data['confirm_password']

        # check if phone is validated
        phone = PhoneOtp.objects.filter(phone=serializer.data['phone'])
        phone = phone.last()
        if phone and phone.validated:
            # password validation
            pass_format = re.compile(
                "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
            )
            password_valid = re.match(pass_format, password)
            if password_valid:
                if password == c_password:

                    return Response({
                        # "user": DoctorRegisterSerializer(user, context=serializer.data),
                        "message": "User created successfully!"
                    })

                else:
                    return Response({
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Password is not Matching!"
                    })

            else:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must contain minimum 8 digit Alphanumeric character!"
                })

        else:
            # verification not successful
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Phone no is not verified! Please verify your phone number through otp."
            })


class DoctorRegisterEmail(APIView):
    """
    View to register Doctor using email
    :parameter: email, password, confirm_password, name, image, nid, vehicle
    """

    serializer_class = DoctorEmailRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # password validation
        password = serializer.data['password']
        c_password = serializer.data['confirm_password']
        pass_format = re.compile(
            "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        )
        password_valid = re.match(pass_format, password)
        if password_valid:
            if password != c_password:
                # error
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password is not Matching!"
                })
        else:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Password must contain minimum 8 digit Alphanumeric character!"
            })

        # email validation
        user_obj = User.objects.filter(email=serializer.data['email'])
        print(user_obj)
        if user_obj.exists():
            print('email exists')
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "The email id is already taken. Please provide different email id!"
            })

        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            # send token
            user = User.objects.get(username=request.data['email'])
            token = send_token(user, request)

            return Response({
                # 'data': serializer.data,
                'status': status.HTTP_201_CREATED,
                "message": "Registration successful!!",
                'email': request.data['email'],
                'token': token,
                'timestamp': datetime.datetime.now(),
            })
        return Response({
            'error': serializer.error_messages,
            'status': status.HTTP_400_BAD_REQUEST
        })


def send_token(user, request):
    """ Token is mailed to given email id"""
    domain = request.META['HTTP_HOST'],
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    generated_token = account_activation_token.make_token(user)
    protocol = request.scheme
    token = protocol + "://" + domain[0] + '/activate/' + uid + '/' + generated_token
    # Email generation
    subject = "Please Activate Your Account"
    message = render_to_string('activation-request.html', {'user': user, 'token': token})
    user.email_user(subject, message, from_email=settings.EMAIL_HOST_USER)
    return token


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    View to Generate Token
    """

    # TIMEOUT_DAYS = 7(Default)
    def _make_hash_value(self, user, timestamp):
        return (
                text_type(user.pk) + text_type(timestamp)
        )


account_activation_token = AccountActivationTokenGenerator()


class ProfileActivate(APIView):

    def get(self, request, *args, **kwargs):
        """
        By redirecting to confirmation link, user profile is activated
        """
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # checking if the user exists, if the token is valid.
        if user is not None and account_activation_token.check_token(user, kwargs['token']):
            # if valid set active True
            user.is_active = True
            user.save()
            return Response({
                # 'data': serializer.data,
                'status': status.HTTP_200_OK,
                "message": "Profile is activated",
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Invalid Token!",
            })


class CustomTokenObtainPairView(TokenObtainPairView):
    """ Login in view for user """
    serializer_class = CustomTokenObtainPairSerializer


class UserVerificationView(APIView):
    """
    Upon receiving an identity image, user is verified
    :parameter: user_id, identity_image
    """
    serializer_class = VerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(pk=serializer.data['user_id'])
                user.is_verified = True
                user.save()
            except User.DoesNotExist as error:
                data = {'message': "User is not found"}
                return Response(data, status.HTTP_400_BAD_REQUEST)

            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'user verified',
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorProfileView(viewsets.ModelViewSet):
    """ Doctor profile view """
    # permission_classes = (IsAuthenticated)
    serializer_class = DoctorSerializer
    queryset = DoctorsProfile.objects.all()

    def get_queryset(self):
        return DoctorsProfile.objects.filter(user=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        Doctor profile Update Api - PUT Request
        URL: /user/Doctor/profile/update/
        :parameter: email, phone, image, org_name, org_type, owner_name, business_id
        """
        partial = kwargs.pop('partial', False)
        instance = DoctorsProfile.objects.filter(user=self.request.user.id)
        serializer = self.serializer_class(instance.first(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(serializer)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response({
            'profile': serializer.data,
            'message': "profile updated successfully!"
        })

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class UserVerify(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        By redirecting to this link, checks if user is registered with email or phone.
        If registered with phone, sends otp to verify.
        If registered with email, sends verification link to email
        """
        # check is registered using email or phone
        username = request.user.username
        if '@' in username:
            # user is registered with email
            # send token
            token = send_token_email(request.user, request.user.email, request)
            print(token)
            return Response({
                'verification_method': 'email',
                'message': 'Email is sent to verify your account!',
            })
        else:
            # user is registered with phone
            # sends otp
            phone = request.user.phone
            otp = generate_otp(phone)
            if otp:
                # checks if otp for this phone number already exists
                old = PhoneOtp.objects.filter(phone=phone).last()
                if old:
                    old.valid = False
                    old.save()

                phone_otp = PhoneOtp.objects.create(phone=phone, otp=otp)
                phone_otp.save()
            return Response({
                'verification_method': 'phone',
                'message': 'otp sent',
                'otp': phone_otp.otp
            })


class EmailUpdateView(viewsets.ModelViewSet):
    """
    Email update view for user
    :parameter: email
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailUpdateSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        email Update Api - PUT Request
        URL: /user/email/update/
        :parameter: email
        """
        partial = kwargs.pop('partial', False)
        instance = User.objects.filter(pk=self.request.user.id)
        serializer = self.serializer_class(instance.first(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # updating user email and username
        email = serializer.data['email']
        if email:
            user = User.objects.get(pk=request.user.id)
            # if username == email, update username
            if request.user.email == request.user.username:
                user.username = serializer.data['email']
            user.email = serializer.data['email']
            user.save()
            msg = "Email id is updated successfully!"
        else:
            msg = "Please enter new Email id!"

        return Response({
            'id': request.user.id,
            'email': serializer.data['email'],
            'message': msg
        })

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


def send_token_email(user, new_email, request):
    """ Verification link is mailed to given email id to verify"""
    domain = request.META['HTTP_HOST'],
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    generated_token = account_activation_token.make_token(user)
    protocol = request.scheme
    token = protocol + "://" + domain[0] + '/verify/' + uid + '/' + generated_token
    # Email generation
    subject = "Please Verify Your Account To Update Email id"
    message = render_to_string('verification-request.html', {'user': user, 'token': token})
    user.email_user(subject, message, from_email=settings.EMAIL_HOST_USER)
    return token


class EmailVerify(APIView):

    def get(self, request, *args, **kwargs):
        """ By redirecting to this link, email is verified"""
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # checking if the user exists, if the token is valid.
        if user is not None and account_activation_token.check_token(user, kwargs['token']):
            return Response({
                'status': status.HTTP_200_OK,
                "message": "Profile is verified",
                "is_verified": True
            })
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                "message": "Invalid Token!",
                "is_verified": False
            })


class PhoneUpdateView(viewsets.ModelViewSet):
    """
    Phone update view for user
    :parameter: phone
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneUpdateSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        print("user")
        return User.objects.filter(pk=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        Phone Update Api - PUT Request
        URL: /user/phone/update/
        :parameter: phone
        """
        partial = kwargs.pop('partial', False)
        instance = User.objects.filter(pk=self.request.user.id)
        serializer = self.serializer_class(instance.first(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # updating user phone and username
        phone = serializer.data['phone']
        if phone:
            user = User.objects.get(pk=request.user.id)
            # if username == phone, update username
            if request.user.phone == request.user.username:
                user.username = serializer.data['phone']
            user.phone = serializer.data['phone']
            user.save()
            msg = "Phone number is updated successfully!"
        else:
            msg = "Please enter new phone number!"

        return Response({
            'id': request.user.id,
            'phone': serializer.data['phone'],
            'message': msg
        })

    def partial_update(self, request, *args, **kwargs):
        print("partial update")
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class PasswordUpdateView(APIView):
    """
    Password update view for user
    :parameter: current_password, new_password, confirm_password
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordUpdateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get user
            user = User.objects.get(pk=request.user.id)
            # check if password matched
            current_password = user.check_password(serializer.data['current_password'])
            if current_password:
                # if password matched, check new_password == confirm_password
                if serializer.data['new_password'] == serializer.data['confirm_password']:
                    # set password
                    user.password = make_password(serializer.data['new_password'])
                    user.save()
                    msg = "Password changed successfully"
                else:
                    msg = "Password did not match!"
            else:
                msg = "Current password is incorrect!"
            return Response({
                'message': msg
            })
        else:
            msg = "Please provide valid data to change password!"
            return Response({
                'message': msg
            })


class DoctorListView(generics.ListAPIView):
    """ View to retrieve Doctor list """
    queryset = DoctorsProfile.objects.all()
    serializer_class = DoctorListSerializer


class AddressListView(generics.ListAPIView):
    """
    View to retrieve user address list
    Can be accessed only if authenticated
    """
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]
