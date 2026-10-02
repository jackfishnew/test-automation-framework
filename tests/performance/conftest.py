import pytest
import csv
from pathlib import Path
from utility.factories import make_user_data_abonament_basic
from api.api_clients.api_client_base import ApiClient
from utility.emails import get_activation_token_from_email_body
from utility.factories import make_user_data_abonament_basic
import yaml

BASE_DIR = Path(__file__).resolve().parent
DATA_TEST_USER_PATH = BASE_DIR / "data" / "jmeter_test_users.csv"
TEST_SUITE_PATH = BASE_DIR / "taurus_test_suite.yml"

@pytest.fixture
def jmeter_user_count():
    config_path = TEST_SUITE_PATH
    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    jmeter = next(
        item for item in config["execution"]
        if item.get("executor") == "jmeter"
    )
    return int(jmeter["concurrency"])


@pytest.fixture
def jmeter_new_user_accounts(api_client, jmeter_user_count):
    """Create the account consumed by the JMeter CSV data set."""
    created_users = []
    csv_path = DATA_TEST_USER_PATH
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    for cnt in range(jmeter_user_count):
        user_data = make_user_data_abonament_basic()
        response = api_client.api_register_user(**user_data)
        assert response.status_code == 201, f"Failed to create user: {response.text}"

        activation_token = get_activation_token_from_email_body(user_data["email"])
        response = api_client.api_activate_user(activation_token)
        assert response.status_code == 302, f"Failed to activate user: {response.text}"

        with csv_path.open(mode="a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=("username", "password"))
            if cnt == 0:
                writer.writeheader()
            writer.writerow({"username": user_data["email"], "password": user_data["password"]})
        created_users.append(user_data)
    assert len(created_users) == jmeter_user_count


@pytest.fixture
def jmeter_remove_user_accounts(auth_api_client_admin):
    # cleanup - remove user
    csv_path = DATA_TEST_USER_PATH
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            response = auth_api_client_admin.api_delete_user(row["username"])
            assert response.status_code == 200, f"Failed to delete user: {response.text}"
    if csv_path.exists():
        csv_path.unlink()
    assert not csv_path.exists()