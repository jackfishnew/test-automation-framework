import functools
import os
from typing import Dict, Optional
import pytest
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from urllib.parse import urljoin



def skip_on_connection_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestsConnectionError as exc:
            pytest.skip(f"API not reachable: {exc}")
    return wrapper



class ApiClient:
    def __init__(self, base_url, api_tokens: Optional[Dict[str, str]] = None):
        self._session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self._api_tokens = None
        
        # Trigger the method during init
        self.set_api_tokens(api_tokens)

    def set_api_tokens(self, api_tokens: Optional[Dict[str, str]]) -> None:
        """Updates internal tokens and applies the Authorization header."""
        self._api_tokens = api_tokens
        
        if api_tokens and "access" in api_tokens:
             self._session.headers.update({"Authorization": f"Bearer {self._api_tokens['access']}"})
        else:
            self._session.headers.pop("Authorization", None)

    def get_api_token(self):
        return self._api_tokens['access']
    
    @skip_on_connection_error
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        return self._session.request(method, url, **kwargs)


    #### Tokens ######
    def obtain_tokens(self, username: str, password: str) -> requests.Response:
        payload = {"username": username, "password": password}
        return self._request("post","/api/user_management/token/", json=payload)
    
    def refresh_tokens(self, refresh_token: str) -> requests.Response:
        payload = {"refresh": refresh_token}
        return self._request("post","/api/user_management/token/refresh/", json=payload)
    
    ##### Public endpoints #####
    def api_schema(self):
        headers = {'Authorization': None}
        return self._request('get', "/api/schema/", headers= headers)

    # Creates a new user with default club context and sends an activation email.
    def api_register_user(self, email: str, password: str, accept_terms: bool, accept_privacy_policy: bool, abonament: str) -> requests.Response:
        headers = {'Authorization': None}
        payload = {
            "email": email,
            "password": password,
            "accept_terms": accept_terms,
            "accept_privacy_policy": accept_privacy_policy,
            "abonament": abonament
        }
        return self._request("post","/api/user_management/register/", json=payload, headers=headers)
    
    # Verifies activation token, activates account, and redirects user to frontend login page.
    def api_activate_user(self, token: str) -> requests.Response:
        headers = {'accept': '*/*',
                   'Authorization': None
                   }
        return self._request("get", f"/api/user_management/activate/{token}/", headers=headers, allow_redirects=False)
    
    def api_password_reset(self, email: str) -> requests.Response:
        headers = {'Authorization': None}
        payload = {"email": email}
        return self._request("post","/api/user_management/password_reset/", json=payload, headers=headers)
    
    def api_password_reset_confirm(self, token: str, password: str) -> requests.Response:
        headers = {'Authorization': None}
        payload = {"password": password}
        return self._request("post", f"/api/user_management/password_reset_confirm/{token}/", json=payload, headers=headers)
    



    
class MockApiClient:
    def __init__(self, base_url, mocker):
        self.base_url = base_url.rstrip("/")
        self.mocker = mocker

    # requests_mock patches requests.* so this returns the mocked Response
    def post(self, path: str, *, json: Dict, headers: Dict[str, str] = None, status_code: int) -> requests.Response:
        url = f"{self.base_url}{path}"
        # Register the mocked response
        self.mocker.post(url, json=json, status_code=status_code)
        # Perform the call to get a Response
        return requests.post(url, json=json, headers=headers)

    def obtain_tokens(self, username: str, password: str):
        expected_user = os.getenv("TEST_API_USERNAME")
        expected_pass = os.getenv("TEST_API_PASSWORD")
        if username == expected_user and password == expected_pass: 
            returned_data = {"access": "mock-access", "refresh": "mock-refresh"} 
            return self.post("/api/user_management/token/", json=returned_data, status_code=200)
        else:
            returned_data = {"detail": "Invalid credentials"}
            return self.post("/api/user_management/token/", json=returned_data, status_code=401)


