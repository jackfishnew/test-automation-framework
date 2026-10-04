from typing import Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
import pytest
import warnings

T = TypeVar("T", bound=BaseModel)

def assert_response(
    response,
    expected_status: int = 200,
    schema: Optional[Type[T]] = None
) -> Optional[T]:
    """Validates Status Code (Layer 1), Content-Type (Layer 2), and Schema (Layer 3)."""
    
    # Layer 1: Status Code
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        # By including response.text, it dumps the actual body of the HTTP response into your console.
        #  When an API fails (like returning a 400 Bad Request), the server usually sends back a JSON
        #  payload explaining why it failed (e.g., "Missing email field"). Including response.text saves you
        #  from having to rerun the test with a debugger just to see that error message.
        f"Response body: {response.text}"
    )

    # Layer 2: 
    if expected_status in (301, 302):
        # Verify redirect location header is present
        assert "Location" in response.headers, "Expected 'Location' header for redirect response"
        

    # Content-Type Header (skip for 204 No Content) 
    elif expected_status != 204:
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"Expected 'application/json' in header, got '{content_type}'"
        )

    # Layer 3: Schema Validation
    if schema:
        try:
            return schema.model_validate(response.json())
        except ValidationError as e:
            pytest.fail(f"API Contract broken for {schema.__name__}:\n{e}")
        except ValueError:
            pytest.fail(f"Response body is not valid JSON: {response.text}")
    else:
        warnings.warn(f"Schema check is off!", UserWarning)

    # safety guard used to prevent your program from crashing when an API sends back an empty response.
    return response.json() if response.text else None