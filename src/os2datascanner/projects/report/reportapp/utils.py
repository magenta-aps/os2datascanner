import json
import hashlib
import structlog

from django.conf import settings
from django.contrib.auth.models import User

from os2datascanner.engine2.pipeline import messages

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


def get_or_create_user_aliases(user_data):  # noqa: D401
    """Hook called after user is created, during SAML login, in DB and before login.
    This method creates or updates the users aliases depending on if new user_data
    has arrived or the old the user_data has been updated.

    The django-saml plugin takes care of the basic user_data such as email, username etc.
    So we do not need to worry about creating or updating the django user."""

    saml_attr = settings.SAML2_AUTH.get('ATTRIBUTES_MAP')
    username = get_user_data(saml_attr.get('username'), user_data)
    email = get_user_data(saml_attr.get('email'), user_data)
    sid = get_user_data(saml_attr.get('sid'), user_data)
    user = User.objects.get(username=username)
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


def iterate_queryset_in_batches(batch_size, queryset):
    i = 0
    count = queryset.count()
    while i < count:
        print('i: {}'.format(str(i)))
        batch = queryset[i: batch_size + i]
        yield batch
        i += batch_size


def get_max_sens_prop_value(doc_report_obj, key):
    """Helper method for migration 0014_documentreport_added_sensitivity_and_probability.
    This method returns either a Sensitivity object or probability maximum value.
    The method is located in utils as could become handy else where."""
    if (doc_report_obj.data
            and "matches" in doc_report_obj.data
            and doc_report_obj.data["matches"]):
        return getattr(messages.MatchesMessage.from_json_object(
            doc_report_obj.data["matches"]), key)
