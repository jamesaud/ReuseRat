# -*- coding: utf-8 -*-
"""
Django settings for ReuseRat project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ

ROOT_DIR = environ.Path(__file__) - 3  # (reuserat/config/settings/common.py - 3 = reuserat/)
APPS_DIR = ROOT_DIR.path('reuserat')

env = environ.Env()
env.read_env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Useful template tags:
    'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'django_pdfkit',
    'allauth',  # Registration
    'allauth.account',  # Registration
    'allauth.socialaccount',  # Registration
    'localflavor', # Django LocalFlavor
)

# Add Any Third Party apps that need to come before django built in apps.
DJANGO_APPS = ('flat_responsive',) + DJANGO_APPS

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'reuserat.users.apps.UsersConfig',
    'reuserat.shipments.apps.ShipmentsConfig',
    'reuserat.shopify.apps.ShopifyConfig',
    'reuserat.knowledge.apps.KnowledgeConfig',
    'reuserat.stripe.apps.StripeConfig',

)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reuserat.custom_middleware.middleware.FixMissingStripeAccountMiddleWare',
)



# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'reuserat.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')


# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""James Audretsch""", 'trashandtreasure67@gmail.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///reuserat'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
                "reuserat.context_processors.project_processors.variables",
            ],
            'libraries' : {
                'project_tags': 'reuserat.template_tags.tags',
            }
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
    str(ROOT_DIR('bower_components')),
    str(ROOT_DIR('node_modules')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


# Some really nice defaults

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_USERNAME_REQUIRED = False


ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'reuserat.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'reuserat.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# ------------------------------------------------------------------------------
INSTALLED_APPS += (
    # Social auth providers
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    )



# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'



# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

SOCIALACCOUNT_PROVIDERS = \
    {'facebook':
       {'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile', 'user_friends'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC':  lambda request: 'en_US',
        'VERIFIED_EMAIL': True,
        'VERSION': 'v2.4'},
    'google':
       {'METHOD': 'oauth2',
        'SCOPE': ['email'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC':  lambda request: 'en_US',
        'VERIFIED_EMAIL': True,
        'VERSION': 'v2.4'}
        }



# CUSTOM PROJECT SETTINGS
# ------------------------------------------------------------------------------

# Exposed in reuserat.context_processors.project_processors.variables function
EXTERNAL_URLS = {
    'SOCIAL':
        {'reddit': 'https://www.reddit.com/user/reuserat/',
         'facebook': 'https://www.facebook.com/pg/ReuseRat-1624736247551484/',
         'twitter': 'https://twitter.com/ReuseRat',
         'medium': 'https://medium.com/reuserat'},
    'SITE':{
        'store': 'https://reuserat.com',
        'seller': 'https://sell.reuserat.com',
        'blog': 'https://reuserat.com/blogs/news',
        'schedule_pickup': 'https://reuserat-pickup.youcanbook.me',
        'schedule_boxes': 'https://reuserat.youcanbook.me'}
}

# Set Production to false
PRODUCTION = False


# ENV LOADED KEYS AND SETTINGS
# ------------------------------------------------------------------------------

# For shopify webhooks
SHOPIFY_WEBHOOK_API_KEY = env('SHOPIFY_WEBHOOK_API_KEY')

# What comes between "www" and ".com" eg. for www.reuserat.com it would be 'reuserat'
SHOPIFY_DOMAIN_NAME = env('SHOPIFY_DOMAIN_NAME', default='reuserat')
SHOPIFY_APP_NAME = env('SHOPIFY_APP_NAME', default='sell-stuff-get-paid.myshopify.com')

SHOPIFY_API_KEY = env('SHOPIFY_API_KEY')
SHOPIFY_APP_API_SECRET = SHOPIFY_API_KEY

SHOPIFY_PASSWORD = env('SHOPIFY_PASSWORD')

# What comes between "www" and ".com" eg. for www.reuserat.com it would be 'reuserat'
SHOPIFY_DOMAIN_NAME = env('SHOPIFY_DOMAIN_NAME', default='reuserat')


SPLIT_PERCENT_PER_SALE = .5  # A number from 0 to 1, how much the customer gets for each item sold.

# Stripe Company Account API Keys.
# See your keys here: https://dashboard.stripe.com/account/apikeys
STRIPE_SECRET_KEY  = env('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')

# Fake test Stripe data
STRIPE_TEST_ACCOUNT_NUMBER = '000123456789'
STRIPE_TEST_ROUTING_NUMBER = '111000025'

# Paypal Production
PAYPAL_CLIENT_ID=env('PAYPAL_CLIENT_ID', default=None)
PAYPAL_SECRET=env('PAYPAL_SECRET', default=None)

PAYPAL_SANDBOX_BUYER_EMAIL = env('PAYPAL_SANDBOX_BUYER_EMAIL', default="trashandtreasure67-buyer@gmail.com")
PAYPAL_MODE = env('PAYPAL_MODE') # Or Production


# Check API Lob
LOB_LIVE_API_KEY=env('LOB_LIVE_API_KEY')
LOB_TEST_API_KEY=env('LOB_TEST_API_KEY', default=None)
LOB_API_VERSION = env('LOB_API_VERSION', default=None)

# For the Shipping 'TO' address
WAREHOUSE_NAME = 'ReuseRat Inc.'
WAREHOUSE_ADDRESS_LINE = '504 E Cottage Grove'
WAREHOUSE_ZIP = '47408'
WAREHOUSE_CITY = 'Bloomington'
WAREHOUSE_STATE = 'IN'

# For the 'FROM' address for checks
COMPANY_NAME = 'ReuseRat Inc.'
COMPANY_ADDRESS_LINE = '504 E Cottage Grove'
COMPANY_ADDRESS_LINE_APT= 'Apt #5'
COMPANY_ZIP = '47408'
COMPANY_CITY = 'Bloomington'
COMPANY_STATE = 'IN'

