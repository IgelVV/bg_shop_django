from .base import *


DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': DATABASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB'),
        'USER': getenv('POSTGRES_USER'),
        'PASSWORD': getenv('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432,
    }
}