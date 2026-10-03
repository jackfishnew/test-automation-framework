import uuid
from ui.constants import DEFAULT_DISPLAY_VIEWPORT, DEFAULT_MOBILE_VIEWPORT
from api.api_clients.api_client_base import ApiClient, MockApiClient
import schemathesis 

def make_user_data_abonament_basic() -> dict:
    """Generate dynamic payload for user creation."""
    unique_id = uuid.uuid4().hex[:8]
    data = {
        "email": f"testuser_{unique_id}@test.local",
        "password": "test_password123!",
        "accept_terms": True,
        "accept_privacy_policy": True,
        "abonament": "basic"
    }
    return data



def make_display_size(mobile):
    return DEFAULT_MOBILE_VIEWPORT if mobile else DEFAULT_DISPLAY_VIEWPORT 

def get_schema(api_url: str, method: str):
    return schemathesis.pytest.from_fixture("api_schema").include(path=api_url, method=method)