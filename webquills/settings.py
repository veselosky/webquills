"""
Django settings for webquills project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import environ

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Read environment-specific settings from environment variables
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))  # Use a .env file if present
env = environ.Env()


#######################################################################
# Application Composition: Fixed values regardless of environment.
#######################################################################

# The order of installed apps determines the search order for templates.
# Template loader uses first template it finds, so in order to override
# templates from 3rd parties, list our apps first, stock stuff last.
INSTALLED_APPS = [
    # Our apps
    "webquills.core",
    "webquills.search",
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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.core.middleware.SiteMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ]
        },
    }
]

ROOT_URLCONF = "webquills.urls"
WSGI_APPLICATION = "webquills.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = "en-US"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [os.path.join(PROJECT_DIR, "static")]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

#######################################################################
# CONFIGURATION: Varies by environment.
#######################################################################
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR}/db.sqlite3")}
CACHES = {"default": env.cache(default="locmemcache://")}
# Email settings don't use a dict. Add to local vars instead.
# https://django-environ.readthedocs.io/en/latest/#email-settings
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)

#
# Wagtail settings
#
WAGTAIL_SITE_NAME = env("WAGTAIL_SITE_NAME", default="WebQuills")

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = env("WAGTAIL_BASE_URL", default="http://example.com")


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
