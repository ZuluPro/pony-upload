from django.conf import settings

def get_setting(key, default):
    key = 'PONY_UPLOAD_' + key
    value = getattr(settings, key, default)
    return value

LEASE_TIMEOUT = get_setting('LEASE_TIMEOUT', 3600)
