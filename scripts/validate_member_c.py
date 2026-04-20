from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml

# Allow running this script directly from scripts/ while importing app package.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.slo_alerts import evaluate_alerts, evaluate_slos


SLO_PATH = Path("config/slo.yaml")
ALERT_PATH = Path("config/alert_rules.yaml")
RUNBOOK_PATH = Path("docs/alerts.md")

REQUIRED_SLIS = {"latency_p95_ms", "error_rate_pct", "daily_cost_usd", "quality_score_avg"}
REQUIRED_ALERTS = {"high_latency_p95", "high_error_rate", "cost_budget_spike"}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _slugify_heading(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _extract_heading_slugs(md_path: Path) -> set[str]:
    if not md_path.exists():
        return set()
    slugs: set[str] = set()
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip()
        if heading:
            slugs.add(_slugify_heading(heading))
    return slugs


def validate_slo() -> tuple[bool, list[str]]:
    issues: list[str] = []
    cfg = _load_yaml(SLO_PATH)
    slis = cfg.get("slis") if isinstance(cfg.get("slis"), dict) else {}

    if not cfg:
        return False, [f"Missing or invalid YAML: {SLO_PATH}"]

    if not cfg.get("service"):
        issues.append("Missing service in config/slo.yaml")
    if not cfg.get("window"):
        issues.append("Missing window in config/slo.yaml")

    missing = REQUIRED_SLIS - set(slis.keys())
    if missing:
        issues.append(f"Missing SLI(s): {', '.join(sorted(missing))}")

    for sli_name, spec in slis.items():
        if not isinstance(spec, dict):
            issues.append(f"SLI {sli_name} must be an object")
            continue
        if "objective" not in spec:
            issues.append(f"SLI {sli_name} missing objective")
        if "target" not in spec:
            issues.append(f"SLI {sli_name} missing target")

    # Ensure evaluator can consume config with runtime metric keys.
    sample_metrics = {
        "latency_p95": 2500,
        "error_rate_pct": 1.0,
        "daily_cost_usd": 1.5,
        "quality_avg": 0.8,
    }
    result = evaluate_slos(sample_metrics, SLO_PATH)
    if set(result.get("slis", {}).keys()) != set(slis.keys()):
        issues.append("evaluate_slos output does not match configured SLI keys")

    return len(issues) == 0, issues


def validate_alerts() -> tuple[bool, list[str]]:
    issues: list[str] = []
    cfg = _load_yaml(ALERT_PATH)
    alerts = cfg.get("alerts") if isinstance(cfg.get("alerts"), list) else []

    if not cfg:
        return False, [f"Missing or invalid YAML: {ALERT_PATH}"]

    if len(alerts) < 3:
        issues.append("Need at least 3 alert rules")

    alert_names = {a.get("name") for a in alerts if isinstance(a, dict)}
    missing_alerts = REQUIRED_ALERTS - {name for name in alert_names if isinstance(name, str)}
    if missing_alerts:
        issues.append(f"Missing required alert(s): {', '.join(sorted(missing_alerts))}")

    heading_slugs = _extract_heading_slugs(RUNBOOK_PATH)

    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        name = str(alert.get("name", "unknown"))
        for key in ("severity", "condition", "owner", "runbook"):
            if not alert.get(key):
                issues.append(f"Alert {name} missing field: {key}")

        runbook = str(alert.get("runbook", ""))
        if runbook:
            if "#" not in runbook:
                issues.append(f"Alert {name} runbook must include anchor (#...)")
            else:
                file_part, anchor = runbook.split("#", 1)
                runbook_file = Path(file_part)
                if not runbook_file.exists():
                    issues.append(f"Alert {name} runbook file missing: {runbook_file}")
                elif anchor not in heading_slugs:
                    issues.append(f"Alert {name} runbook anchor not found: #{anchor}")

    # Ensure all conditions are parsable by evaluator and aligned with runtime metrics.
    sample_metrics = {
        "latency_p95": 5500,
        "latency_p95_ms": 5500,
        "error_rate_pct": 7.5,
        "hourly_cost_usd": 0.7,
    }
    evaluated = evaluate_alerts(sample_metrics, ALERT_PATH)
    unsupported = [a["name"] for a in evaluated.get("alerts", []) if a.get("evidence") == "condition_not_supported"]
    if unsupported:
        issues.append(f"Unsupported alert condition syntax: {', '.join(sorted(unsupported))}")

    return len(issues) == 0, issues


def validate_runtime(base_url: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    endpoints = {
        "/metrics": ["traffic", "latency_p95", "error_rate_pct", "hourly_cost_usd"],
        "/slo": ["overall_status", "slis"],
        "/alerts": ["total", "alerts"],
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            for endpoint, required_keys in endpoints.items():
                response = client.get(f"{base_url}{endpoint}")
                if response.status_code != 200:
                    issues.append(f"{endpoint} returned {response.status_code}")
                    continue
                payload = response.json()
                missing = [k for k in required_keys if k not in payload]
                if missing:
                    issues.append(f"{endpoint} missing keys: {', '.join(missing)}")
    except Exception as exc:
        issues.append(f"Runtime check failed: {exc}")

    return len(issues) == 0, issues


def _print_check(title: str, passed: bool, issues: list[str]) -> None:
    state = "PASS" if passed else "FAIL"
    print(f"[{state}] {title}")
    for issue in issues:
        print(f"  - {issue}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Member C deliverables (SLO + Alerts)")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL for runtime API checks")
    parser.add_argument("--check-runtime", action="store_true", help="Also validate /metrics, /slo, /alerts endpoints")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any check fails")
    args = parser.parse_args()

    slo_pass, slo_issues = validate_slo()
    alerts_pass, alerts_issues = validate_alerts()

    runtime_pass = True
    runtime_issues: list[str] = []
    if args.check_runtime:
        runtime_pass, runtime_issues = validate_runtime(args.base_url)

    print("=== Member C Validation ===")
    _print_check("SLO config", slo_pass, slo_issues)
    _print_check("Alert rules + runbook", alerts_pass, alerts_issues)
    if args.check_runtime:
        _print_check("Runtime endpoints", runtime_pass, runtime_issues)

    overall = slo_pass and alerts_pass and (runtime_pass if args.check_runtime else True)
    print(f"\nOverall: {'PASS' if overall else 'FAIL'}")

    if args.strict and not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
