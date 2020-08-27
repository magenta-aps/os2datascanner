DEBUG = True

ALLOWED_HOSTS = []

SITE_URL = 'localhost:8040'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gdf_g)jKJhgf7&IL78yrfiuuhGH0i^bac=jh+je!!=jlsejbj9'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'os2datascanner_report',
        'USER': 'os2datascanner_report_dev',
        'PASSWORD': 'os2datascanner_report_dev',
        'HOST': 'db',
    }
}

DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_size': 5,
    'recycle': 300
}

# Email settings
DEFAULT_FROM_EMAIL = 'os2datascanner@INSERT_DOMAIN_NAME'
ADMIN_EMAIL = 'os2datascanner@INSERT_DOMAIN_NAME'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# The name of the institution, to be included in the notification signoff
NOTIFICATION_INSTITUTION = 'MAGENTA APS'

SAML2_ENABLED = False

# The full documentation can be found here: https://github.com/fangli/django-saml2-auth
SAML2_AUTH = {
    # Metadata is required, choose either remote url or local file path
    'METADATA_AUTO_CONF_URL': '[The auto(dynamic) metadata configuration URL of SAML2]',
    'METADATA_LOCAL_FILE_PATH': '[The metadata configuration file path]',

    # Optional settings below
    'DEFAULT_NEXT_URL': '/admin',  # Custom target redirect URL after the user get logged in. Default to /admin if not set. This setting will be overwritten if you have parameter ?next= specificed in the login URL.
    'CREATE_USER': 'TRUE', # Create a new Django user when a new user logs in. Defaults to True.
    'NEW_USER_PROFILE': {
        'USER_GROUPS': [],  # The default group name when a new user logs in
        'ACTIVE_STATUS': True,  # The default active status for new users
        'STAFF_STATUS': True,  # The staff status for new users
        'SUPERUSER_STATUS': False,  # The superuser status for new users
    },
    'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
        'email': 'Email',
        'username': 'UserName',
        'first_name': 'FirstName',
        'last_name': 'LastName',
    },
    'TRIGGER': {
        'CREATE_USER': 'path.to.your.new.user.hook.method',
        'BEFORE_LOGIN': 'path.to.your.login.hook.method',
    },
    'ASSERTION_URL': 'https://mysite.com', # Custom URL to validate incoming SAML requests against
    'ENTITY_ID': 'https://mysite.com/saml2_auth/acs/', # Populates the Issuer element in authn request
    'NAME_ID_FORMAT': 'FormatString', # Sets the Format property of authn NameIDPolicy element
    'USE_JWT': False, # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
    'FRONTEND_URL': 'https://myfrontendclient.com', # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
}
