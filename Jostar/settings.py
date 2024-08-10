import os
from pathlib import Path
from datetime import timedelta
from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-l=yr^p+x5^3l0a#x$^39w1a4s0*i33@^=8%f@w&6un^t@b1a7z'
CRYPTOGRAPHY_SECRET_KEY = Fernet.generate_key()

DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'users',
    'jostars',
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

ROOT_URLCONF = 'Jostar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('JOSTAR_DB_NAME'),
        'USER': os.getenv('JOSTAR_DB_USER'),
        'PASSWORD': os.getenv('JOSTAR_DB_PASSWORD'),
        'HOST': os.getenv('JOSTAR_DB_HOST'),
        'PORT': os.getenv('JOSTAR_DB_PORT'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.JostarUser'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Authorization header using the Bearer scheme. Example: `Bearer {token}`",
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

# KAFKA SETTINGS
KAFKA_BOOTSTRAP_SERVER_ADDRESS = os.getenv('KAFKA_BOOTSTRAP_SERVER_ADDRESS', 'localhost:9092')
JOSTARS_RATING_KAFKA_TOPIC = os.getenv('JOSTARS_RATING_KAFKA_TOPIC', 'jostar_ratings_v2')
KAFKA_RATINGS_CONSUMER_BATCH_SIZE = os.getenv('KAFKA_RATINGS_CONSUMER_BATCH_SIZE', 2)
# REDIS SETTINGS
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_CACHE_TIMEOUT = os.getenv('REDIS_CACHE_TIMEOUT')

# Rete weight adjustor
MAX_NORMAL_RATING_COUNT_IN_ONE_HOUR = os.getenv('MAX_NORMAL_RATING_COUNT_IN_ONE_HOUR', 50)
RATING_WEIGHT_DOWNGRADING_FACTOR = os.getenv('RATING_WEIGHT_DOWNGRADING_FACTOR', 0.01)
RATING_WEIGHT_NORMALIZER_FACTOR = os.getenv('RATING_WEIGHT_DOWNGRADING_FACTOR', 1.648)

# Website settings
JOSTAR_URL = os.getenv('JOSTAR_URL', 'jostar.ir')
