from abc import ABC

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from rest_framework.response import Response

from .models import User, DoctorsProfile, PhoneOtp, UserAddress


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'is_active', 'is_verified']
        extra_kwargs = {
        }


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone']
        extra_kwargs = {
        }


class UserAddressSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserAddress
        fields = ['user', 'address', 'city', 'postal_code', 'country']
        extra_kwargs = {
        }


class PhoneValidateSerializer(serializers.Serializer, ABC):
    phone = serializers.CharField(max_length=100)


class OtpValidateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=100)
    otp = serializers.CharField(max_length=4)

    class Meta:
        model = PhoneOtp
        fields = ['phone', 'otp', 'created_at']
        extra_kwargs = {
        }


class DoctorRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.CharField()

    class Meta:
        model = DoctorsProfile
        fields = ['id', 'phone', 'password', 'confirm_password', 'org_name', 'org_type', 'image',
                  'nid_no', 'doctors_id', 'address', 'city', 'postal_code', 'country']
        extra_kwargs = {
        }

    def create(self, validated_data):
        # saving user detail
        user = User.objects.create_user(username=validated_data['phone'], phone=validated_data['phone'],
                                        password=validated_data['password'], seller=True)
        user.save()

        # saving address detail
        address = UserAddress.objects.filter(user=user).first()
        address.address = validated_data['address']
        address.city = validated_data['city']
        address.postal_code = validated_data['postal_code']
        address.country = validated_data['country']
        address.save()
        user.address = address
        user.save()

        # saving seller detail
        doctor = DoctorsProfile.objects.get(user=user)
        doctor.org_name = validated_data['org_name']
        doctor.org_type = validated_data['org_type']
        doctor.image = validated_data['image']
        doctor.nid_no = validated_data['nid_no']
        doctor.doctors_id = validated_data['doctors_id']
        doctor.address = address
        doctor.save()
        return user


class DoctorEmailRegisterSerializer(serializers.ModelSerializer):
    """
      A seller serializer to return the seller details
    """
    email = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.CharField()

    class Meta:
        model = DoctorsProfile
        fields = (
            'email', 'password', 'confirm_password', 'org_name', 'org_type', 'image', 'nid_no',
            'doctors_id',
            'address', 'city', 'postal_code', 'country')

    def create(self, validated_data):
        """
        :param validated_data: data containing all the details of seller
        :return: returns a successfully created seller record
        """
        # user = User.objects.create_user(username=validated_data.pop('email'), email=validated_data.pop('email'),
        #                                 password=make_password(validated_data.pop('password')), seller=True)

        user = User.objects.create_user(username=validated_data['email'], email=validated_data['email'],
                                        password=(validated_data['password']), seller=True,
                                        is_active=False)
        user.save()

        # saving address detail
        address = UserAddress.objects.filter(user=user).first()
        address.address = validated_data['address']
        address.city = validated_data['city']
        address.postal_code = validated_data['postal_code']
        address.country = validated_data['country']
        address.save()

        # saving seller detail
        doctor = DoctorsProfile.objects.get(user=user)
        doctor.org_name = validated_data['org_name']
        doctor.org_type = validated_data['org_type']
        doctor.image = validated_data['image']
        doctor.nid_no = validated_data['nid_no']
        doctor.doctors_id = validated_data['doctors_id']
        doctor.address = address
        doctor.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer, ABC):
    """ TokenObtainPairSerializer is customized to allow authorization by phone/email """

    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get("password")
        }

        # checking if username matches with email or phone
        user_obj = User.objects.filter(Q(email=attrs.get('username')) | Q(phone=attrs.get("username"))).first()
        if user_obj:
            credentials['username'] = user_obj.username
        data = super(CustomTokenObtainPairSerializer, self).validate(credentials)
        # updating response data
        data.update({'id': self.user.id})
        data.update({'detail': 'Login Successful!'})
        data.update({'is_verified': self.user.is_verified})
        return data


class VerificationSerializer(serializers.Serializer, ABC):
    user_id = serializers.IntegerField()
    identity_image = serializers.ImageField()


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    full_address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    postal_code = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    address = UserAddressSerializer(required=False)

    class Meta:
        model = DoctorsProfile
        fields = ('user', 'image', 'org_name', 'org_type', 'doctors_id', 'full_address', 'city',
                  'postal_code', 'country', 'address')
        extra_kwargs = {
            'org_name': {'required': False},
            'org_type': {'required': False},
            'doctors_id': {'required': False},
        }

    def update(self, instance, validated_data):
        address = instance.address

        address.address = validated_data.get('full_address', address.address)
        address.city = validated_data.get('city', address.city)
        address.postal_code = validated_data.get('postal_code', address.postal_code)
        address.country = validated_data.get('country', address.country)
        address.save()

        instance.image = validated_data.get('image', instance.image)
        instance.org_name = validated_data.get('org_name', instance.org_name)
        instance.org_type = validated_data.get('org_type', instance.org_type)
        instance.doctors_id = validated_data.get('doctors_id', instance.doctors_id)
        instance.save()
        return instance


class EmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def update(self, instance, validated_data):
        # check if email id is taken
        email_obj = User.objects.filter(Q(email=validated_data.get('email'))).exclude(pk=instance.pk)
        print(email_obj)
        if email_obj.exists():
            return Response({
                'message': "This email id is already taken!",
            })
        else:
            instance.email = validated_data.get('email', instance.email)
            return instance


class PhoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    def update(self, instance, validated_data):
        # check if phone is taken
        phone_obj = User.objects.filter(Q(phone=validated_data.get('phone'))).exclude(pk=instance.pk)
        print(phone_obj)
        if phone_obj.exists():
            return Response({
                'message': "This phone number is taken!",
            })
        else:
            instance.phone = validated_data.get('phone', instance.phone)
            return instance


class PasswordUpdateSerializer(serializers.Serializer, ABC):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        print("attrs")
        return attrs


class DoctorListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = DoctorsProfile
        fields = ('id', 'user', 'org_name', 'org_type')
