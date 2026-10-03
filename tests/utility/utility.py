import pytest
from pathlib import Path
import os
import platform
from urllib.parse import urljoin, urlsplit

from functools import lru_cache
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from api.api_clients.api_client_base import ApiClient

def get_url_ui(url_fragment: str):
    ui_base_url = os.getenv("TEST_UI_BASE_URL")
    return  urljoin(ui_base_url, url_fragment)

def fetch_and_validate_tokens(client: ApiClient, credentials: dict) -> dict:
    response = client.obtain_tokens(**credentials)
    assert response.status_code == 200, f"Token endpoint failed: {response.status_code} {response.text}"
    data = response.json()
    for key in ("access", "refresh"):
        assert key in data, f"Missing {key} token in response"
    return data

# Helper to get option or env var
def get_option_env(config: pytest.Config, option: str, env_var: str) -> str:
    value = config.getoption(option)
    if value:
        return value
    env_value = os.getenv(env_var)
    if env_value:
        return env_value
    raise RuntimeError(f"Missing required setting: pass {option} or set {env_var}")


# Load .env files if present
def load_env_files() -> None:
    """Load .env from project root or tests folder so os.getenv can see TEST_API_* variables."""
    here = Path(__file__).resolve()
    root = here.parents[2]
    candidates = [root / ".env", root / "tests" / ".env", root / "tests" / "api" / ".env"]

    def parse(path: Path) -> None:
        if not path.exists():
            return
        for line in path.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value

    for candidate in candidates:
        parse(candidate)

# 
def normalize_bool(value: object | None) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

# Internal helpers to get browser 
def get_browser(pytestconfig: pytest.Config) -> str:
    cli_value = pytestconfig.getoption("--ui-browser")
    if cli_value:
        return cli_value.lower()
    env_value = os.getenv("UI_BROWSER")
    if env_value:
        return env_value.lower()
    return "chrome"

# Internal helpers to get headless settings
def get_headless(pytestconfig: pytest.Config) -> bool:
    cli_value = pytestconfig.getoption("--ui-headless")
    if cli_value is not None:
        return normalize_bool(cli_value)
    env_value = os.getenv("UI_HEADLESS")
    if env_value is not None:
        return normalize_bool(env_value)
    return normalize_bool(os.getenv("CI"))

@lru_cache(maxsize=1)
def _get_chromedriver_path() -> str:
    """Download/locate ChromeDriver binary exactly once per test process."""
    return ChromeDriverManager().install()

def build_chrome_driver(headless: bool, width, length) -> webdriver.Chrome:
    options = ChromeOptions()

    options.add_argument(f"--window-size={width},{length}")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    if platform.system() == "Linux":
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    service = ChromeService(_get_chromedriver_path())
    return webdriver.Chrome(service=service, options=options)


# Internal helpers to build browser drivers
def build_firefox_driver(headless: bool, width, length) -> webdriver.Firefox:
    options = FirefoxOptions()
    options.add_argument(f"--window-size={width},{length}")
    if headless:
        options.add_argument("--headless")

    # Check if running in a CI/CD environment or if the local driver file exists
    is_ci = os.getenv("CI", "false").lower() == "true"
    local_path = "c:\\D\\GitHubPrivat\\Klubster\\drivers\\geckodriver-v0.37.1-win64\\geckodriver.exe"

    if is_ci or not os.path.exists(local_path):
        service = FirefoxService(executable_path=GeckoDriverManager().install())
    else:
        gecko_path = "c:\\D\\GitHubPrivat\\Klubster\\drivers\\geckodriver-v0.37.1-win64\\geckodriver.exe"  # Windows example: "C:\\drivers\\geckodriver.exe"
        service = FirefoxService(executable_path=gecko_path)

    # 3. If Firefox browser is installed in a non-standard location, set its binary path:
    # options.binary_location = "/path/to/firefox/executable"

    return webdriver.Firefox(service=service, options=options)

def resolve_jmeter_target(api_url: str) -> tuple[str, str, str]:
    """Normalize an API URL into protocol, host and port values for JMeter.

    GitHub Codespaces proxy URLs like https://<hash>-8000.app.github.dev do not expose
    an explicit port in the host, so it should remain empty instead of being forced to 443.
    """
    value = (api_url or "").strip().rstrip("/")
    if not value:
        return "http", "localhost", "80"

    parsed = urlsplit(value if "://" in value else f"http://{value}")
    protocol = parsed.scheme or "http"
    host = parsed.hostname or "localhost"

    if parsed.port is not None:
        port = str(parsed.port)
    elif host.endswith(".app.github.dev"):
        port = ""
    elif protocol == "http":
        port = "80"
    else:
        port = ""

    return protocol, host, port
