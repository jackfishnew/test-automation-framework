from utility.assertions import assert_response
import pytest
import allure


@allure.epic("User Management API")
@allure.feature("User profile")
@pytest.mark.api
class TestUserProfile:

    @pytest.fixture
    def expected_profile_defaults(self):
        """Default static fields and permissions expected for a basic user."""
        return {
            "abonament": "basic",
            "user_type": "abonament",
            "roles": ["administrator"],
            "permissions": [
                "zarzadzanie_klubem",
                "platnosci_zajec_pokaz",
                "platnosci_zajec_edycja",
                "aktualnosci_dodawanie_watku",
                "aktualnosci_edycja_watku",
                "aktualnosci_komentowanie",
                "komunikacja",
                "zarzadzanie_rezerwacjami",
                "rezerwacje",
                "kalendarz_klubowy_zarzadzanie",
                "kalendarz_klubowy_ogladanie",
            ],
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "must_accept_legal": False,
        }
    

    def test_get_user_profile_returns_200(
        self, auth_api_client, new_user_account, expected_profile_defaults
    ):
        # Act
        response = auth_api_client.get_profile()
        parsed_response = assert_response(response=response, expected_status=200)

        # 1. Assert account specific identity fields
        expected_email = new_user_account["email"]
        assert parsed_response["username"] == expected_email
        assert parsed_response["email"] == expected_email
        assert isinstance(parsed_response["profile_id"], int)

        # 2. Assert static default profile fields & permissions
        for key, expected_value in expected_profile_defaults.items():
            assert parsed_response[key] == expected_value, f"Mismatch on key: '{key}'"
    
    def test_get_user_profile_not_authenticated_returns_401(self, no_auth_api_client):
        # Prepare
        paylaod = {
            "detail": "Authentication credentials were not provided."
        }
        response = no_auth_api_client.get_profile()
        parsed_response = assert_response(response=response, expected_status=401)
        assert parsed_response.get("detail") == paylaod.get("detail")


    def test_accept_legal_terms_returns_200(self, auth_api_client, new_user_account):
        # Prepare
        payload = {
            "accept_terms": True,
            "accept_privacy_policy": True
        }
        reposnse = auth_api_client.accept_legal_terms(payload)
        parsed_response = assert_response(response=reposnse, expected_status=200)
        assert parsed_response.get("message") == 'Akceptacja została zapisana.'

        # Check if data were correctly saved
        response = auth_api_client.get_profile()
        parsed_response = assert_response(response=response, expected_status=200)
        assert parsed_response.get("terms_accepted")
        assert parsed_response.get("privacy_policy_accepted")


    @pytest.mark.parametrize(
        "payload",
        [
            # Explicit False flags
            {"accept_terms": False, "accept_privacy_policy": False},
            {"accept_terms": False, "accept_privacy_policy": True},
            {"accept_terms": True, "accept_privacy_policy": False},
            # Missing keys entirely
            {"accept_privacy_policy": True},  # missing accept_terms
            {"accept_terms": True},           # missing accept_privacy_policy
            {},                               # missing both
        ],
        ids=["both_false", "terms_false", "privacy_false", "missing_terms", "missing_privacy", "empty_payload"]
    )
    def test_accept_legal_terms_returns__legal_acceptance_flags_missing_or_false__returns_400(self, auth_api_client, new_user_account, payload):
        # Prepare
        response = auth_api_client.accept_legal_terms(payload)
        parsed_response = assert_response(response=response, expected_status=400)
        assert parsed_response.get("error") == 'Aby kontynuować, zaakceptuj regulamin i politykę prywatności.'


    def test_accept_legal_terms__not_authenticated__returns_401(self, no_auth_api_client, new_user_account):
        # Prepare
        payload = {
            "accept_terms": True,
            "accept_privacy_policy": True
        }
        response = no_auth_api_client.accept_legal_terms(payload)
        parsed_response = assert_response(response=response, expected_status=401)
        assert parsed_response.get("detail") == 'Authentication credentials were not provided.'

    @pytest.mark.api
    @pytest.mark.parametrize(
            "paylaod",
            [
                {
                    "permissions": [
                        "zarzadzanie_klubem",
                        "platnosci_zajec_pokaz",
                        "platnosci_zajec_edycja",
                    ],
                }
            ], ids=["permissions"]
    )
    def test_update_user_profile__returns_200(self, auth_api_client, new_user_account, paylaod):
        auth_api_client.profile_update(paylaod)
        response = assert_response(response=auth_api_client.profile_update(paylaod), expected_status=200)
        assert response.get("message") == "Profil został zaktualizowany pomyślnie."

        # Check if changed
        parsed_response = assert_response(response=auth_api_client.get_profile(), expected_status=200)
        for key, expected_value in paylaod.items():
            assert parsed_response.get(key) == expected_value, f"Mismatch on key: '{key}'"

        