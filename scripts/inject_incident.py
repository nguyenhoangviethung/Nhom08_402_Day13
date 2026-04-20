from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
INCIDENTS_PATH = Path("data/incidents.json")
SCENARIOS = ["rag_slow", "tool_fail", "cost_spike"]


def load_incident_descriptions() -> dict[str, str]:
    if not INCIDENTS_PATH.exists():
        return {}
    return json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))


def fetch_status(base_url: str, timeout: float) -> dict:
    response = httpx.get(f"{base_url}/health", timeout=timeout)
    response.raise_for_status()
    return response.json()


def print_status(base_url: str, timeout: float) -> None:
    body = fetch_status(base_url, timeout)
    incidents = body.get("incidents", {})
    print("--- Incident Status ---")
    for name in SCENARIOS:
        print(f"{name}: {incidents.get(name, False)}")


def print_scenarios() -> None:
    descriptions = load_incident_descriptions()
    print("--- Available Incidents ---")
    for name in SCENARIOS:
        detail = descriptions.get(name, "No description available.")
        print(f"{name}: {detail}")


def toggle_incident(base_url: str, scenario: str, disable: bool, timeout: float) -> None:
    action = "disable" if disable else "enable"
    response = httpx.post(f"{base_url}/incidents/{scenario}/{action}", timeout=timeout)
    response.raise_for_status()
    body = response.json()
    print(f"{action.upper()} {scenario}: {body}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enable, disable, or inspect demo incident toggles.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Target app base URL")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    parser.add_argument("--scenario", choices=SCENARIOS, help="Incident scenario name")
    parser.add_argument("--disable", action="store_true", help="Disable the selected incident")
    parser.add_argument("--status", action="store_true", help="Show the current incident status")
    parser.add_argument("--list", action="store_true", help="List incidents and their descriptions")
    args = parser.parse_args()

    if args.list:
        print_scenarios()

    if args.status:
        print_status(args.base_url, args.timeout)

    if args.scenario:
        toggle_incident(args.base_url, args.scenario, args.disable, args.timeout)
        print_status(args.base_url, args.timeout)
        return

    if not args.list and not args.status:
        parser.error("Provide --scenario, --status, or --list.")


if __name__ == "__main__":
    main()
