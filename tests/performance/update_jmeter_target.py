import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utility.utility import resolve_jmeter_target


def update_jmeter_target(config_path: str | None = None, api_url: str | None = None) -> None:
    """Update Taurus JMeter scenario target based on TEST_API_BASE_URL."""
    config_path = config_path or str(Path(__file__).resolve().parent / "taurus_test_suite.yml")
    api_url = api_url or os.getenv("TEST_API_BASE_URL", "http://127.0.0.1:8000")

    protocol, host, port = resolve_jmeter_target(api_url)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    jmeter_scenario = config.setdefault("scenarios", {}).get("jmeter-test")
    if jmeter_scenario is None:
        raise KeyError("scenarios.jmeter-test not found in Taurus config")

    properties = jmeter_scenario.setdefault("properties", {})
    properties["protocol"] = protocol
    properties["host"] = host
    properties["port_nr"] = int(port) if port else ""

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)


if __name__ == "__main__":
    update_jmeter_target()
