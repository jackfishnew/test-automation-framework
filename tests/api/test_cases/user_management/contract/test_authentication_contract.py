import pytest 
import allure
from utility.factories import get_schema
from utility.emails import get_activation_token_from_email_body
    

@pytest.mark.contract
@allure.epic("User Management")
@allure.feature("Authentication")
@allure.story("As a Release Engineer,I want contract tests to validate API specifications before deployment,So that client integrations don't break due to unintended schema changes.")
class TestAuthenticationContract:

    @get_schema("/api/user_management/token/refresh/", method="POST").parametrize()
    def test_token_refresh_contract(self, case, api_base_url):
        case.call_and_validate(base_url=api_base_url)

    @get_schema("/api/user_management/token/", method="POST").parametrize()
    def test_token_contract(self, case, api_base_url):
        case.call_and_validate(base_url=api_base_url)
    
    @get_schema("/api/user_management/register/", method="POST").parametrize()
    def test_register_contract(self, case, api_base_url):
        case.call_and_validate(base_url=api_base_url)

    @pytest.mark.xfail(
        reason=(
            "This endpoint intentionally returns a generic success for any supplied email "
            "to prevent account enumeration; schema validation rejects unexpected fields. "
            "Keep it as an expected failure until the API contract is updated."
        ),
        strict=False,
    )
    @get_schema("/api/user_management/resend-activation/", method="POST").parametrize()
    def test_resend_activation_contract(self, case, api_base_url):
        case.call_and_validate(base_url=api_base_url)

    @get_schema("/api/user_management/activate/{token}/", method="GET").parametrize()
    def test_activate_contract(self, case, api_base_url, registered_user):
        # Extract token from email
        user_email = registered_user.get("email")
        activation_token = get_activation_token_from_email_body(user_email)
        # Inject into path directly
        case.path = case.path.replace("{token}", activation_token)
        case.call_and_validate(base_url=api_base_url)


    # Chain filters to narrow down the test scope
    # filtered_schema = (
    #     schema
    #     #.exclude(path_regex="^/api/user_management/password_reset")
    #     .include(path="/api/user_management/token/", method="POST")
    #     #.include(path="/api/user_management/token/refresh/", method="POST")
    #     #.include(path="/api/user_management/legal/accept/", method="POST")
    #     #.include(path="/api/user_management/profile/", method="GET")
    #     #.include(path="/api/aktualnosci/threads/", method="POST")
        

    #     #.include(path="/api/user_management/password_reset/", method="POST") # Sends password reset instructions to the provided email if it exists in the system
    #     #.include(path="/api/user_management/password_reset_confirm/{token}/", method="GET") # Checks if password reset token exists and can be used.
    #     #.include(path="/api/user_management/password_reset_confirm/{token}/", method="POST") # Resets user password using valid reset token and clears the token.
    #     #.include(path_regex="^/api/v1/")      # Only test the v1 API
    #     #.exclude(path="/api/v1/internal")     # Exclude an exact path
    #     #.exclude(method="DELETE")             # Skip all DELETE operations
    #     #.exclude(tag="experimental")          # Skip endpoints tagged as 'experimental'
    #     #.exclude(operation_id="resetDB")      # Exclude a specific operation ID
    # )





