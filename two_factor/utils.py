from base64 import b32encode
from django.conf import settings
from django.contrib.admin import sites
from django.shortcuts import redirect
from two_factor.models import PhoneDevice

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from django_otp import devices_for_user


def default_device(user):
    if not user or user.is_anonymous():
        return
    for device in devices_for_user(user):
        if device.name == 'default':
            return device


def backup_devices(user):
    if not user or user.is_anonymous():
        return ()
    return (device for device in devices_for_user(user)
            if device.name == 'backup')


def backup_phones(user):
    if not user or user.is_anonymous():
        return PhoneDevice.objects.empty()
    return user.phonedevice_set.filter(name='backup')


def get_otpauth_url(alias, key):
    b32_key = b32encode(key)
    return 'otpauth://totp/%s?secret=%s' % (alias, b32_key.decode('ascii'))


def get_qr_url(alias, seed):
    return "https://chart.googleapis.com/chart?" + urlencode({
        "chs": "200x200",
        "chld": "M|0",
        "cht": "qr",
        "chl": get_otpauth_url(alias, seed)
    })


def patch_admin_login():
    def redirect_admin_login(self, request):
        return redirect(settings.LOGIN_URL)
    sites.AdminSite.login = redirect_admin_login