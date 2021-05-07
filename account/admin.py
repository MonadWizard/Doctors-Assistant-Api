from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorsProfile, PhoneOtp, UserAddress


class UserPanel(BaseUserAdmin):
    list_display = (
        'username', 'email')
    search_fields = ('email', 'username',)
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# Register your models here.
admin.site.register(User, UserPanel)
admin.site.register(DoctorsProfile)
admin.site.register(PhoneOtp)
admin.site.register(UserAddress)
