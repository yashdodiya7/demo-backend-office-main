from datetime import timedelta
from pathlib import Path
import cloudinary

# Cloudinary config
cloudinary.config(cloud_name='dxwxpfxgi',
                  api_key='913467956416832',
                  api_secret='s9bP_rjDlqfor6uIniWsIPi_3B0')

# API KEYS
TWOFACTOR_API_KEY = "b9bf68ef-fa2d-11ee-8cbb-0200cd936042"

# Stripe key
STRIPE_PUBLISHABLE_KEY = "pk_test_51P8GTRSHvWfLAe0cstoDlCEGTQ0eOqbJK8oSI8zbVnRHiezy3nbEnlL3dTuUZBkLmvYaMujrLdSivy7vaAr37izH00mkZWpUjj"

STRIPE_SECRET_KEY = "sk_test_51P8GTRSHvWfLAe0cwXoZ17FttK8XecGTljj9404t6dYGSDYYC2RU1isB8r1Q6YcdcQOEzuyU7YTBY2XcuqmCj6iz00TzyRU5nC"

STRIPE_PRICE_ID_BASIC = 'price_1P8hZDSHvWfLAe0cOpXo7Ifx'
STRIPE_PRICE_ID_PREMIUM = 'price_1PAn0eSHvWfLAe0ctPQoUEJO'

STRIPE_ENDPOINT_SECRET = "whsec_5778d1cb8da7402d19e6ecf0289c53cf49b81637b148ced4ac1cdb488e5f1db8"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6b$4s*9epi3f_*p@m8+i)3jk#qxgv8@2p-aw-$ve*u*)s=g-o4"

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yashdodiya501@gmail.com'
EMAIL_HOST_PASSWORD = 'wbtf zaae yqzt bgcr'
DEFAULT_FROM_EMAIL = 'nestmates@gmail.com'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

# CELERY_BROKER_URL = 'amqp://localhost'  # Assuming local message broker
# CELERY_RESULT_BACKEND = 'django_celery_beat.backends.database:DatabaseBackend'
#
# CELERY_BEAT_SCHEDULE = {
#     'check_subscriptions': {
#         'task': 'payments.tasks.check_and_update_subscriptions',
#         'schedule': '0 0 * * *',  # Runs daily at midnight
#     },
# }

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "user",
    "listing",
    "payments",
    "phoneverify",

    "phone_verify",
    "rest_framework",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# SMS verification twillio

PHONE_VERIFICATION = {
    'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',
    'OPTIONS': {
        'SID': 'ACf2cd7ce768a181058e7bd738ff423d66',
        'SECRET': '41aeb2b42316ee807a6bda8e39610fe6',
        'FROM': '+12564748549',
        'SANDBOX_TOKEN': '123456',
    },
    'TOKEN_LENGTH': 6,
    'MESSAGE': 'Welcome to Mates! Please use security code {security_code} to proceed.',
    'APP_NAME': 'Phone Verify',
    'SECURITY_CODE_EXPIRATION_TIME': 3600,  # In seconds only
    'VERIFY_SECURITY_CODE_ONLY_ONCE': False,
    # If False, then a security code can be used multiple times for verification
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'backend',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.User"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
