from pathlib import Path

from django.conf.locale.en import formats


formats.DATETIME_FORMAT = "d.m.Y H:i"

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = False
# Application definition

INSTALLED_APPS = [
    # "django.contrib.admin",
    "core.apps.MyAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    # third-party apps
    "corsheaders",
    "django_singleton_admin",
    "safedelete",
    "django_celery_beat",
    "django_celery_results",
    "djoser",
    # Apps
    "game",
    "orders",
    "users",
    "office",
    "print",
    "stats",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
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

WSGI_APPLICATION = "core.wsgi.application"


REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "core.settings.common.exceptions.api_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSIONS_CLASSES": ("rest_framework,permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}


AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)


# Password validation

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


AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR.parent / "public" / "static"
ASSETS = BASE_DIR.parent / "public" / "assets"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # where from serve media

# Celery app config

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"
CELERY_BROKER_URL = "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/1"
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_RESULT_BACKEND = "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/1"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "#/username/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": False,
    "SERIALIZERS": {},
}

# Покупки AppStore GoogleMarket
APPLE_IN_APP_PURCHASES_V2 = {
    75: "ru.rdp.giftsolitaire.deck4",
    50: "ru.rdp.giftsolitaire.deck3",
    25: "ru.rdp.giftsolitaire.deck2",
    0: "ru.rdp.giftsolitaire.deck",
}

GOOGLE_IN_APP_PURCHASES_V2 = {
    75: "purchase_deck_75",
    50: "purchase_deck_50",
    25: "purchase_deck_25",
    0: "purchase_deck",
}


INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ORIGIN_ALLOW_ALL = (
    True  # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
)
CORS_ALLOW_CREDENTIALS = True
APPEND_SLASH = True
