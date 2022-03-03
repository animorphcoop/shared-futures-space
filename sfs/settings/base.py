# pyre-strict
"""
Django settings for sfs project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from typing import List, Dict, TypedDict, Optional, Union

class Template(TypedDict):
    BACKEND: str
    DIRS: List[str]
    APP_DIRS: bool
    OPTIONS: Dict[str, Union[str, List[str]]]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
PROJECT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR: str = os.path.dirname(PROJECT_DIR)
sys.path.append(os.path.normpath(os.path.join(BASE_DIR, 'apps')))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# Application definition
# add apps/ to the Python path

INSTALLED_APPS: List[str] = [    
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'landing',
    'dashboard',
    'userauth',
    'messaging',
    'action',
    'project',
    'search',
    'core',


    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',


    'tailwind',
    'theme',
    'django_browser_reload',
    'widget_tweaks',

    'django_htmx',

]

MIDDLEWARE: List[str] = [


    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    'django_htmx.middleware.HtmxMiddleware',

    "django_browser_reload.middleware.BrowserReloadMiddleware",

]

ROOT_URLCONF: str = 'sfs.urls'

TEMPLATES: List[Template] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/userauth'),
            os.path.join(BASE_DIR, 'templates/project'),
        ],
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

WSGI_APPLICATION: str = 'sfs.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES: Dict[str, Dict[str,Optional[str]]] = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # these are in app_variables.env:
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS: List[Dict[str,str]] = [
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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE: str = 'en-us'

TIME_ZONE: str = 'UTC'

USE_I18N: bool = True

USE_L10N: bool = True

USE_TZ: bool = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS: List[str] = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS: List[str] = [
    os.path.join(PROJECT_DIR, 'static'),
    os.path.join(BASE_DIR, 'apps/theme/static'),
    os.path.join(BASE_DIR, 'templates/ts_output'),

]

# Account
ACCOUNT_FORMS = {'signup': 'userauth.forms.CustomSignupForm'}
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE: str = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT: str = os.path.join(BASE_DIR, 'static')
STATIC_URL: str = '/static/'

MEDIA_ROOT: str = os.path.join(BASE_DIR, 'media')
MEDIA_URL: str = '/media/'

# Wagtail settings

WAGTAIL_SITE_NAME: str = "sfs"

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL: str = 'https://dev.sharedfutures.space'

# for @login_required
LOGIN_URL = '/account/login/'

# Redis & Celery configuration
CELERY_BROKER_URL: str = "redis://redis:6379"
CELERY_RESULT_BACKEND: str = "redis://redis:6379"

WAGTAIL_USER_EDIT_FORM: str = 'userauth.forms.CustomUserEditForm'
WAGTAIL_USER_CREATION_FORM: str = 'userauth.forms.CustomUserCreationForm'
WAGTAIL_USER_CUSTOM_FIELDS: List[str] = ['display_name', 'year_of_birth', 'post_code']

# urls are not strings! domain.com/page and domain.com/page/ are the same url
# unfortunately these settings don't seem to work, so urls are in fact strings for our purposes until we can figure out why :(
APPEND_SLASH = False
WAGTAIL_APPEND_SLASH = False

TAILWIND_APP_NAME = 'theme'
