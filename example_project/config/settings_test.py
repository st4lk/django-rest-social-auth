" Settings for tests. "
INSTALLED_APPS = []

from .settings import *  # NOQA: E402

# Databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

if 'knox' not in INSTALLED_APPS:
    INSTALLED_APPS += ('knox', )
