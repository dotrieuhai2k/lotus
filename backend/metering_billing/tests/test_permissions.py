from unittest.mock import MagicMock

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from metering_billing.exceptions import NoAPIKeyProvided
from metering_billing.permissions import ValidOrganization, HasUserAPIKey
from metering_billing.serializers.serializer_utils import OrganizationUUIDField


@pytest.fixture
def permission_test_common_setup(
        generate_org_and_api_key,
        add_users_to_org,
        api_client_with_api_key_auth,
        add_customers_to_org,
):
    def do_permission_test_common_setup():
        # set up organizations and api keys
        org, key = generate_org_and_api_key("test-org")
        org2, key2 = generate_org_and_api_key("test-org-2")
        setup_dict = {
            "org": org,
            "key": key,
            "org2": org2,
            "key2": key2,
        }
        # client with no auth
        client_no_auth = APIClient()
        setup_dict["client_no_auth"] = client_no_auth

        # client with api key auth
        client_api_key = api_client_with_api_key_auth(key)
        setup_dict["client_api_key"] = client_api_key

        # client with not exist api key
        client_ne_api_key = APIClient()
        client_ne_api_key.credentials(HTTP_X_API_KEY="HTTP_X_API_KEY")
        setup_dict["client_ne_api_key"] = client_ne_api_key

        # client with session auth
        client_session_auth = APIClient()
        (user_org,) = add_users_to_org(org, n=1)
        client_session_auth.force_authenticate(user=user_org)
        setup_dict["user_org"] = user_org
        setup_dict["client_session_auth"] = client_session_auth

        # client with api key auth and session auth of user in org
        client_11 = api_client_with_api_key_auth(key)
        client_11.force_authenticate(user=user_org)
        setup_dict["client_11"] = client_11

        # client with api key auth of org and session auth of user in org2
        client_12 = api_client_with_api_key_auth(key)
        (user_org2,) = add_users_to_org(org2, n=1)
        client_12.force_authenticate(user=user_org2)
        setup_dict["client_12"] = client_12

        (customer_org_1,) = add_customers_to_org(org, n=1)
        (customer_org_2,) = add_customers_to_org(org2, n=1)
        setup_dict["customer_org_1"] = customer_org_1
        setup_dict["customer_org_2"] = customer_org_2

        view = MagicMock()
        setup_dict["view"] = view
        request = MagicMock()
        setup_dict["request"] = request

        return setup_dict

    return do_permission_test_common_setup


@pytest.mark.django_db(transaction=True)
class TestValidOrganization:

    def test_valid_organization_in_api(self, permission_test_common_setup):
        setup_dict = permission_test_common_setup()
        # no auth
        response = setup_dict["client_no_auth"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Authentication credentials were not provided."
        # api key do not exist
        response = setup_dict["client_ne_api_key"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Authentication credentials were not provided."
        # api key auth
        response = setup_dict["client_api_key"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_200_OK
        response = setup_dict["client_api_key"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_2"].customer_id})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # session auth
        response = setup_dict["client_session_auth"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_200_OK
        response = setup_dict["client_session_auth"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_2"].customer_id})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # api key auth and session auth of user in org
        response = setup_dict["client_11"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_200_OK
        response = setup_dict["client_11"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_2"].customer_id})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # api key auth of org and session auth of user in org2
        response = setup_dict["client_12"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_1"].customer_id})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = setup_dict["client_12"].get(
            reverse("customer-detail", kwargs={"customer_id": setup_dict["customer_org_2"].customer_id})
        )
        assert response.status_code == status.HTTP_200_OK

    def test_valid_organization_user_session_auth(self, permission_test_common_setup):
        setup_dict = permission_test_common_setup()
        # No auth
        setup_dict["request"].user.is_authenticated = False
        setup_dict["request"].META = {}
        assert ValidOrganization().get_organization(setup_dict["request"]) is None
        assert ValidOrganization().has_permission(setup_dict["request"], setup_dict["view"]) is False
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_1"]
        ) is False
        # Session auth
        setup_dict["request"].user = setup_dict["user_org"]
        assert ValidOrganization().get_organization(setup_dict["request"]) == setup_dict["org"]
        assert ValidOrganization().has_permission(setup_dict["request"], setup_dict["view"])
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_1"]
        )
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_2"]
        ) is False

    def test_valid_organization_user_api_key_auth(self, permission_test_common_setup):
        setup_dict = permission_test_common_setup()
        setup_dict["request"].user.is_authenticated = False
        # Right key
        setup_dict["request"].META = {"HTTP_X_API_KEY": setup_dict["key"]}
        assert ValidOrganization().get_organization(setup_dict["request"]) == setup_dict["org"]
        assert ValidOrganization().has_permission(setup_dict["request"], setup_dict["view"])
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_1"]
        )
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_2"]
        ) is False
        # Wrong key
        setup_dict["request"].META = {"HTTP_X_API_KEY": "HTTP_X_API_KEY"}
        assert ValidOrganization().get_organization(setup_dict["request"]) is None
        assert ValidOrganization().has_permission(setup_dict["request"], setup_dict["view"]) is False
        assert ValidOrganization().has_object_permission(
            setup_dict["request"], setup_dict["view"], setup_dict["customer_org_1"]
        ) is False


@pytest.mark.django_db(transaction=True)
class TestHasAPIKey:
    def test_has_api_key_in_api(self, permission_test_common_setup):
        setup_dict = permission_test_common_setup()
        # No API key
        response = setup_dict["client_no_auth"].get(reverse("ping"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "No API key found in request"
        # Right API key
        response = setup_dict["client_api_key"].get(reverse("ping"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["organization_id"] == OrganizationUUIDField().to_representation(setup_dict["org"].organization_id)
        # Wrong API key
        response = setup_dict["client_ne_api_key"].get(reverse("ping"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_has_api_key_in_class(self, permission_test_common_setup):
        setup_dict = permission_test_common_setup()
        # No API key
        setup_dict["request"].META = {}
        with pytest.raises(NoAPIKeyProvided) as exc_info:
            HasUserAPIKey().get_key(setup_dict["request"])
        assert "No API key found in request" in exc_info.value.args[0]
        # Right API key
        setup_dict["request"].META = {"HTTP_X_API_KEY": setup_dict["key"]}
        assert HasUserAPIKey().get_key(setup_dict["request"]) == setup_dict["key"]
        assert HasUserAPIKey().has_permission(setup_dict["request"], setup_dict["view"]) is True
        # Wrong API key
        setup_dict["request"].META = {"HTTP_X_API_KEY": "HTTP_X_API_KEY"}
        assert HasUserAPIKey().get_key(setup_dict["request"]) == "HTTP_X_API_KEY"
        assert HasUserAPIKey().has_permission(setup_dict["request"], setup_dict["view"]) is False
