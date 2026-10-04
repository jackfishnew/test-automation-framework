import pytest
from utility.utility import get_option_env
from urllib.parse import urljoin
from schemathesis import openapi
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR /  "schema.yml"
PYDANTIC_MODELS_PATH = BASE_DIR / "pydantic_models.py"

@pytest.fixture(scope="session")
def api_schema(pytestconfig):
    """Return api schema from backend"""
    base_url = get_option_env(pytestconfig, "--api-base-url", "TEST_API_BASE_URL")
    api_schema_url = "api/schema/"
    return openapi.from_url(url= urljoin(base_url, api_schema_url))


@pytest.fixture(scope="session")
def generate_pydantic_models(api_client):
    """Generate pydentic models from api schema"""
    
    response = api_client.api_schema()
    assert response.status_code == 200
    
    with open(SCHEMA_PATH, "w") as f:
        f.write(response.text)

    command = [
        "datamodel-codegen",
        "--input",
        str(SCHEMA_PATH),
        "--input-file-type",
        "openapi",
        "--output",
        str(PYDANTIC_MODELS_PATH),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        "3.11",
        "--use-annotated",
        "--use-standard-collections",
        "--strict-nullable",
        "--formatters",
        "black",
        "isort",
        "--openapi-scopes",
        "schemas",
        "paths",
    ]

    # Executes the CLI tool and raises subprocess.CalledProcessError if it fails
    subprocess.run(command, check=True)

    # datamodel-codegen --input schema.yaml --input-file-type openapi --output test/api/pydantic_models.py \
    #               --output-model-type pydantic_v2.BaseModel --target-python-version 3.11 --use-annotated \
    #               --use-standard-collections --strict-nullable --formatters black isort --openapi-scopes schemas paths