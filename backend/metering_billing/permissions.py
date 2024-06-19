import logging

from django.core.cache import cache
from rest_framework import permissions
from rest_framework_api_key.permissions import BaseHasAPIKey

from metering_billing.exceptions import NoAPIKeyProvided
from metering_billing.models import APIToken, Organization
from metering_billing.utils import now_utc

logger = logging.getLogger("django.server")


class APIKey:
    def __init__(self, api_key):
        self.api_key = api_key

    @classmethod
    def from_request(cls, request):
        try:
            api_key = request.META["HTTP_X_API_KEY"]
        except KeyError:
            meta_dict = {k.lower(): v for k, v in request.META.items()}
            if "http_x_api_key".lower() in meta_dict:
                api_key = meta_dict["http_x_api_key"]
            else:
                raise NoAPIKeyProvided("No API key found in request")

        return cls(api_key)

    @property
    def organization(self):
        organization_pk = cache.get(self.api_key)
        if organization_pk:
            return Organization.objects.get(pk=organization_pk)

        try:
            api_token = APIToken.objects.get_from_key(self.api_key)
        except APIToken.DoesNotExist:
            return None

        organization_pk = api_token.organization.pk
        expiry_date = api_token.expiry_date
        timeout = (
            60 * 60 * 24
            if expiry_date is None
            else (expiry_date - now_utc()).total_seconds()
        )
        cache.set(self.api_key, organization_pk, timeout)
        return api_token.organization


class HasUserAPIKey(BaseHasAPIKey):
    model = APIToken

    def get_key(self, request):
        return APIKey.from_request(request).api_key


class ValidOrganization(permissions.BasePermission):
    """
    Make sure there's a valid organization attached
    """

    def has_permission(self, request, view):
        request.organization = self.get_organization(request)
        return request.organization is not None

    @staticmethod
    def get_organization(request):
        if request.user.is_authenticated:
            organization = request.user.organization
            return organization

        try:
            api_key = APIKey.from_request(request)
        except NoAPIKeyProvided:
            return None
        else:
            return api_key.organization

    def has_object_permission(self, request, view, obj):
        from metering_billing.models import Organization

        # Instance must have an attribute named `owner`.
        org = request.organization
        if org is None and request.user.is_authenticated:
            org = request.user.organization
        if isinstance(obj, Organization):
            return obj == org
        return obj.organization == org
