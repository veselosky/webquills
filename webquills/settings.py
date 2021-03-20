"""
Django settings for worktracker project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get environment settings
env = environ.Env()
DOTENV = BASE_DIR / ".env"
if DOTENV.exists() and not env("IGNORE_ENV_FILE", default=False):
    environ.Env.read_env(DOTENV.open())

#######################################################################
# Integrations/Resources: settings likely to vary between environments
#######################################################################
# SECRET_KEY intentionally has no default, and will error if not provided
# in the environment. This ensures you don't accidentally run with an
# insecure configuration in production.
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
SQLITE_DB = BASE_DIR / "var" / "db.sqlite3"
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{SQLITE_DB}")}
CACHES = {"default": env.cache("CACHE_URL", default="dummycache://")}
# Email settings don't use a dict. Add to local vars instead.
# https://django-environ.readthedocs.io/en/latest/#email-settings
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "var" / "static"
if not STATIC_ROOT.exists():
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "var" / "media"
if not MEDIA_ROOT.exists():
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

#######################################################################
# Wagtail settings
#######################################################################
WAGTAIL_SITE_NAME = env("WAGTAIL_SITE_NAME", default="WebQuills")

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = env("WAGTAIL_BASE_URL", default="http://localhost.webquills.com")
WAGTAILIMAGES_IMAGE_MODEL = "webquills.AttributableImage"


#######################################################################
# Application Composition: Fixed values regardless of environment.
#######################################################################
ROOT_URLCONF = "webquills.urls"
WSGI_APPLICATION = "webquills.wsgi.application"

# The order of installed apps determines the search order for templates.
# Template loader uses first template it finds, so in order to override
# templates from 3rd parties, list our apps first, stock stuff last.
INSTALLED_APPS = [
    # Our apps
    "webquills.theme_bs4_2021",
    "webquills.core",
    "webquills.search",
    # third party apps
    "bootstrap4",
    # Wagtail extras
    "wagtail.contrib.modeladmin",
    "wagtail.contrib.settings",
    "wagtailfontawesome",
    # Stock wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "modelcluster",
    "taggit",
    # core Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    # Do security stuff in Apache, not Django.
    # https://docs.djangoproject.com/en/3.1/ref/middleware/#django.middleware.security.SecurityMiddleware
    #    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Set this in Apache, not Django.
    # https://docs.djangoproject.com/en/3.1/ref/clickjacking/
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

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
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "wagtail.contrib.settings.context_processors.settings",
            ]
        },
    }
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = "en-US"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


#######################################################################
# DEVELOPMENT: If running in a dev environment, loosen restrictions
# and add debugging tools.
#######################################################################
if DEBUG:
    INSTALLED_APPS.append("wagtail.contrib.styleguide")
    try:
        import debug_toolbar  # pylint: disable=unused-import

        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ['127.0.0.1', ]
    except ImportError:
        # Dev tools are optional
        pass

    try:
        import django_extensions  # pylint: disable=unused-import

        INSTALLED_APPS.append("django_extensions")
    except ImportError:
        # Dev tools are optional
        pass

    ALLOWED_HOSTS = ["*"]
