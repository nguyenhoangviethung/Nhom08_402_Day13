from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# Allow running this script directly from scripts/ while importing app package.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.incidents import status as incident_status


SCENARIOS = ("rag_slow", "tool_fail", "cost_spike")
LOAD_TEST_PATH = Path("scripts/load_test.py")
INJECT_PATH = Path("scripts/inject_incident.py")
INCIDENTS_DOC_PATH = Path("data/incidents.json")


def _print_check(title: str, passed: bool, details: list[str]) -> None:
    state = "PASS" if passed else "FAIL"
    print(f"[{state}] {title}")
    for item in details:
        print(f"  - {item}")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def validate_static() -> tuple[bool, list[str]]:
    issues: list[str] = []

    if not LOAD_TEST_PATH.exists():
        issues.append(f"Missing file: {LOAD_TEST_PATH}")
    if not INJECT_PATH.exists():
        issues.append(f"Missing file: {INJECT_PATH}")

    if LOAD_TEST_PATH.exists():
        text = LOAD_TEST_PATH.read_text(encoding="utf-8")
        required_flags = [
            "--base-url",
            "--query-file",
            "--concurrency",
            "--repeat",
            "--timeout",
            "--skip-metrics",
        ]
        for flag in required_flags:
            if flag not in text:
                issues.append(f"load_test missing CLI flag: {flag}")

        required_metrics = [
            "Latency p50",
            "Latency p95",
            "Latency p99",
            "Throughput",
            "fetch_metrics",
        ]
        for token in required_metrics:
            if token not in text:
                issues.append(f"load_test missing expected metric output/token: {token}")

    if INJECT_PATH.exists():
        text = INJECT_PATH.read_text(encoding="utf-8")
        required_tokens = [
            "--scenario",
            "--status",
            "--list",
            '/incidents/{scenario}/{action}',
            "disable",
            "enable",
        ]
        for token in required_tokens:
            if token not in text:
                issues.append(f"inject_incident missing expected token: {token}")

    state_keys = set(incident_status().keys())
    missing_in_state = set(SCENARIOS) - state_keys
    extra_in_state = state_keys - set(SCENARIOS)
    if missing_in_state:
        issues.append(f"app.incidents missing scenario(s): {', '.join(sorted(missing_in_state))}")
    if extra_in_state:
        issues.append(f"app.incidents has extra scenario(s): {', '.join(sorted(extra_in_state))}")

    descriptions = _load_json(INCIDENTS_DOC_PATH)
    if not descriptions:
        issues.append(f"Missing or invalid JSON: {INCIDENTS_DOC_PATH}")
    else:
        for scenario in SCENARIOS:
            if not descriptions.get(scenario):
                issues.append(f"data/incidents.json missing description for: {scenario}")

    return len(issues) == 0, issues


def _chat_payload() -> dict[str, str]:
    return {
        "message": "Please explain monitoring policy and refund in one concise sentence.",
        "user_id": "member_d_validator",
        "feature": "qa",
        "session_id": f"member-d-{int(time.time())}",
    }


def _chat_once(client: httpx.Client) -> tuple[int, float, dict[str, Any]]:
    payload = _chat_payload()
    started = time.perf_counter()
    response = client.post("/chat", json=payload)
    latency_ms = (time.perf_counter() - started) * 1000
    try:
        body = response.json()
    except ValueError:
        body = {}
    return response.status_code, latency_ms, body


def _metrics_snapshot(client: httpx.Client) -> dict[str, Any]:
    response = client.get("/metrics")
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, dict) else {}


def _daily_cost(metrics: dict[str, Any]) -> float:
    value = metrics.get("daily_cost_usd", 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _toggle(client: httpx.Client, scenario: str, enabled: bool) -> None:
    action = "enable" if enabled else "disable"
    response = client.post(f"/incidents/{scenario}/{action}")
    response.raise_for_status()


def _disable_all(client: httpx.Client) -> None:
    for scenario in SCENARIOS:
        _toggle(client, scenario, enabled=False)


def _cost_delta(client: httpx.Client, *, requests: int) -> float:
    before = _daily_cost(_metrics_snapshot(client))
    for _ in range(max(1, requests)):
        _chat_once(client)
    after = _daily_cost(_metrics_snapshot(client))
    return max(0.0, after - before)


def validate_runtime(base_url: str, min_rag_delta_ms: float, min_cost_ratio: float) -> tuple[bool, list[str]]:
    issues: list[str] = []

    try:
        with httpx.Client(base_url=base_url, timeout=20.0) as client:
            health = client.get("/health")
            health.raise_for_status()
            health_body = health.json() if health.headers.get("content-type", "").startswith("application/json") else {}
            incidents = health_body.get("incidents", {}) if isinstance(health_body, dict) else {}
            missing_health_incidents = [name for name in SCENARIOS if name not in incidents]
            if missing_health_incidents:
                issues.append(
                    f"/health missing incident key(s): {', '.join(sorted(missing_health_incidents))}"
                )

            metrics = _metrics_snapshot(client)
            for key in ("traffic", "latency_p95", "error_rate_pct", "daily_cost_usd"):
                if key not in metrics:
                    issues.append(f"/metrics missing key: {key}")

            _disable_all(client)

            # rag_slow should increase end-to-end latency substantially.
            baseline_status, baseline_latency, baseline_body = _chat_once(client)
            if baseline_status != 200:
                detail = baseline_body.get("detail", "unknown") if isinstance(baseline_body, dict) else "unknown"
                issues.append(f"Baseline chat failed with status={baseline_status}, detail={detail}")
            else:
                _toggle(client, "rag_slow", enabled=True)
                slow_status, slow_latency, slow_body = _chat_once(client)
                _toggle(client, "rag_slow", enabled=False)
                if slow_status != 200:
                    detail = slow_body.get("detail", "unknown") if isinstance(slow_body, dict) else "unknown"
                    issues.append(f"rag_slow probe failed with status={slow_status}, detail={detail}")
                else:
                    delta = slow_latency - baseline_latency
                    if delta < min_rag_delta_ms:
                        issues.append(
                            "rag_slow did not increase latency enough: "
                            f"baseline={baseline_latency:.1f}ms, slow={slow_latency:.1f}ms, delta={delta:.1f}ms, "
                            f"required>={min_rag_delta_ms:.1f}ms"
                        )

            # tool_fail should produce server error while enabled, and recover once disabled.
            _toggle(client, "tool_fail", enabled=True)
            fail_status, _, fail_body = _chat_once(client)
            _toggle(client, "tool_fail", enabled=False)
            recover_status, _, recover_body = _chat_once(client)
            if fail_status < 500:
                detail = fail_body.get("detail", "unknown") if isinstance(fail_body, dict) else "unknown"
                issues.append(
                    f"tool_fail did not trigger failure status (status={fail_status}, detail={detail})"
                )
            if recover_status != 200:
                detail = recover_body.get("detail", "unknown") if isinstance(recover_body, dict) else "unknown"
                issues.append(f"System did not recover after disabling tool_fail (status={recover_status}, detail={detail})")

            # cost_spike should increase cost increment ratio vs baseline requests.
            _disable_all(client)
            baseline_cost_delta = _cost_delta(client, requests=2)

            _toggle(client, "cost_spike", enabled=True)
            spike_cost_delta = _cost_delta(client, requests=2)
            _toggle(client, "cost_spike", enabled=False)

            if baseline_cost_delta <= 0:
                issues.append("Baseline cost delta is zero; cannot verify cost_spike ratio reliably")
            else:
                ratio = spike_cost_delta / baseline_cost_delta if baseline_cost_delta else 0.0
                if ratio < min_cost_ratio:
                    issues.append(
                        "cost_spike impact too small: "
                        f"baseline_delta={baseline_cost_delta:.4f}, spike_delta={spike_cost_delta:.4f}, "
                        f"ratio={ratio:.2f}, required>={min_cost_ratio:.2f}"
                    )

    except Exception as exc:
        issues.append(f"Runtime check failed: {exc}")
    finally:
        # Best effort reset so demo starts from a clean state.
        try:
            with httpx.Client(base_url=base_url, timeout=10.0) as cleanup_client:
                _disable_all(cleanup_client)
        except Exception:
            pass

    return len(issues) == 0, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Member D deliverables (load test + incident injection)")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL for runtime API checks")
    parser.add_argument(
        "--min-rag-delta-ms",
        type=float,
        default=1200.0,
        help="Minimum required latency delta for rag_slow incident",
    )
    parser.add_argument(
        "--min-cost-ratio",
        type=float,
        default=2.0,
        help="Minimum required cost ratio (cost_spike_delta / baseline_delta)",
    )
    parser.add_argument("--check-runtime", action="store_true", help="Also validate runtime incident behavior")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any check fails")
    args = parser.parse_args()

    static_pass, static_issues = validate_static()

    runtime_pass = True
    runtime_issues: list[str] = []
    if args.check_runtime:
        runtime_pass, runtime_issues = validate_runtime(
            base_url=args.base_url,
            min_rag_delta_ms=args.min_rag_delta_ms,
            min_cost_ratio=args.min_cost_ratio,
        )

    print("=== Member D Validation ===")
    _print_check("Script + incident config", static_pass, static_issues)
    if args.check_runtime:
        _print_check("Runtime incident behavior", runtime_pass, runtime_issues)

    overall = static_pass and (runtime_pass if args.check_runtime else True)
    print(f"\nOverall: {'PASS' if overall else 'FAIL'}")

    if args.strict and not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
