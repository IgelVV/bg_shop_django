"""
Django settings for bg_shop project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from os import getenv
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(find_dotenv())

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-!2@7xmj*!-=2@(3mqw=t9&abk7zw)ojdzaywc&hmhki6rg!vm9",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
] + getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.0",
]

CSRF_TRUSTED_ORIGINS = getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")

if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

# Application definition

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
]

LOCAL_APPS = [
    'frontend.apps.FrontendConfig',
    'common.apps.CommonConfig',
    'account.apps.AccountConfig',
    'shop.apps.ShopConfig',
    'orders.apps.OrdersConfig',
    'payment.apps.PaymentConfig',
    'api.apps.ApiConfig',
    'dynamic_config.apps.DynamicConfigConfig',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bg_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bg_shop.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB'),
        'USER': getenv('POSTGRES_USER'),
        'PASSWORD': getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L10N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale/'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = str(BASE_DIR / "static")
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
STATIC_URL = 'static/'

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(BASE_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

IMAGE_SUBDIR = "images"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST framework

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    # "EXCEPTION_HANDLER": "styleguide_example.api.exception_handlers.drf_default_with_modifications_exception_handler",
    # # 'EXCEPTION_HANDLER': 'styleguide_example.api.exception_handlers.hacksoft_proposed_exception_handler',
    # "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     "rest_framework.authentication.BasicAuthentication",
    # ],
}

# Sessions

CART_SESSION_ID = 'cart'

# E-mail config

# to write emails to console during the development.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'your_account@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Celery

CELERY_BROKER_URL = getenv("CELERY_BROKER", "amqp://guest:guest@rabbitmq:5672//")

# Payment

# Test payment
PAYMENT_SERVICE_SIGNATURE = "secret key"

# Logging
LOGLEVEL = getenv("DJANGO_LOGLEVEL", "info").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "general.log",
            "level": "DEBUG",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": LOGLEVEL,
            "handlers": [
                # "console",
            ],
        },
    },
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} "
                      "{process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] "
                      "%(module)s %(message)s",
        },
    },
}

# Site config
MAX_IMAGE_SIZE = 2 * 1024 * 1024

POPULAR_PRODUCTS_LIMIT = 8
LIMITED_PRODUCTS_LIMIT = 3

# Default Dynamic config

ORDINARY_DELIVERY_COST = int(getenv("ORDINARY_DELIVERY_COST", "5"))
EXPRESS_DELIVERY_EXTRA_CHARGE = int(
    getenv("EXPRESS_DELIVERY_EXTRA_CHARGE", "10"))
BOUNDARY_OF_FREE_DELIVERY = int(getenv("BOUNDARY_OF_FREE_DELIVERY", "20"))
COMPANY_INFO = getenv("COMPANY_INFO", "lorem")
LEGAL_ADDRESS = getenv("LEGAL_ADDRESS", "baker st. 221b")
MAIN_PHONE = getenv("MAIN_PHONE", "+7(800)555-35-35")
MAIN_EMAIL = getenv("MAIN_EMAIL", "bg_shop@dot.com")


from bg_shop.settings.third_party.debug_toolbar import DebugToolbarSetup

INSTALLED_APPS, MIDDLEWARE = DebugToolbarSetup.do_settings(
    INSTALLED_APPS, MIDDLEWARE)
