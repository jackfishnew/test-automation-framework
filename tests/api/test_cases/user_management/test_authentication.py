import pytest
import allure
from api.pydantic_models import ApiUserManagementTokenPostResponse, ApiUserManagementTokenPostResponse1, TokenRefresh
from utility.assertions import assert_response

@allure.epic("User Management")
@allure.feature("Authentication")
@pytest.mark.api  
class TestTokenObtainUserManagement:

    @allure.story("Obtain token with valid credentails. Endpoint returns 200")
    def test_obtain_token_valid_credentials_returns_200(self, api_client, new_user_account):
        email = new_user_account.get("email")
        password = new_user_account.get("password")
        response = api_client.obtain_tokens(username=email, password=password)
        parsed_response = assert_response(response, expected_status=200, schema=ApiUserManagementTokenPostResponse)
        # Assert Layer 4: Business Logic
        # Verify tokens structurally look like JWTs (Header.Payload.Signature)
        assert len(parsed_response.access.split(".")) == 3, "Access token is not a valid JWT format"
        assert len(parsed_response.refresh.split(".")) == 3, "Refresh token is not a valid JWT format"

    @allure.story("Invalid credentials, token will be not generated. Endpoint returns 401")
    @pytest.mark.parametrize(
        "username,password",
        [
            ("bad_user", "wrong"),
            ("valid_user", "wrongpass"),
        ],
        ids=["unknown-user", "bad-password"],
    )
    def test_token_obtain_invalid_credentials_returns_401(self, api_client, username, password):
        response = api_client.obtain_tokens(username=username, password=password)     
        parsed_response = assert_response(response, expected_status=401, schema=ApiUserManagementTokenPostResponse1)
        # Extract the expected text from the generated Pydantic model
        expected_text = ApiUserManagementTokenPostResponse1.model_fields['detail'].examples[0]
        assert expected_text in parsed_response.detail

    @allure.story("Generate refresh token with valid user credentails. Endpoint returns 200")
    def test_refresh_token_valid_token_returns_200(self, api_client, new_user_account):
        email = new_user_account.get("email")
        password = new_user_account.get("password")
        obtain_response = api_client.obtain_tokens(username=email, password=password)
        parsed_response = assert_response(obtain_response, expected_status=200, schema=ApiUserManagementTokenPostResponse)
        # Try to refresh token
        response = api_client.refresh_tokens(parsed_response.refresh)
        assert_response(response, expected_status=200, schema=TokenRefresh)

    ### TODO: return 401 not documented in Schema ########
    # @pytest.mark.parametrize(
    #     "refresh_token,expected_status",
    #     [
    #         ("invalidtoken123", 401),
    #         ("expiredtoken456", 401),
    #     ],
    # )
    # def test_refresh_token_invalid_credentials_returns_401(self, api_client, refresh_token, expected_status):
    #     response = api_client.refresh_tokens(refresh_token)
    #     assert response.status_code == expected_status
    #     assert_response(response, expected_status=401, schema=TokenRefresh)




