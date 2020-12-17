import json
import hashlib
import unicodedata
import structlog

from django.conf import settings
from django.contrib.auth.models import User
from mozilla_django_oidc import auth

from .models.aliases.emailalias_model import EmailAlias
from .models.aliases.adsidalias_model import ADSIDAlias

logger = structlog.get_logger()


def hash_handle(handle):
    """
    Creates a SHA-512 hash value from the handle string
    and returns the hex value.
    :param handle: handle as json object
    :return: SHA-512 hex value
    """
    return hashlib.sha512(json.dumps(handle).encode()).hexdigest()


class OIDCAuthenticationBackend(auth.OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(OIDCAuthenticationBackend, self).create_user(claims)
        user.username = claims.get('preferred_username', '')
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()
        get_or_create_user_aliases(user, email=claims.get('email', ''), sid=claims.get('sid', ''))

        # self.update_groups(user, claims)

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.password = claims.get('password', 'password')
        user.save()
        get_or_create_user_aliases(user, email=claims.get('email', ''), sid=claims.get('sid', ''))
        # self.update_groups(user, claims)

        return user


def get_or_create_user_aliases(user, email, sid):  # noqa: D401
    """ This method creates or updates the users aliases  """
    if email:
        EmailAlias.objects.get_or_create(user= user, address=email)
    if sid:
        ADSIDAlias.objects.get_or_create(user=user, sid=sid)

def get_user_data(key, user_data):
    """Helper method for retrieving data for a given key."""
    data = None
    try:
        data = user_data.get(key)[0]
    except TypeError:
        logger.warning('User data does not contain '
                       'any value for key {}'.format(key))
    return data
