from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml


DASHBOARD_SPEC_PATH = Path("docs/dashboard-spec.md")
EVIDENCE_PATH = Path("docs/grading-evidence.md")
SLO_PATH = Path("config/slo.yaml")

REQUIRED_PANEL_PATTERNS: dict[str, str] = {
    "latency": r"latency",
    "traffic": r"traffic",
    "error_rate": r"error rate",
    "cost": r"cost",
    "tokens": r"tokens",
    "quality_proxy": r"quality proxy|security proxy|security & reliability",
}

REQUIRED_EVIDENCE_ITEMS: dict[str, str] = {
    "trace_list": r"langfuse trace list",
    "trace_waterfall": r"full trace waterfall|trace waterfall",
    "correlation_log": r"correlation_id",
    "pii_redaction": r"pii redaction",
    "dashboard_6_panels": r"dashboard with 6 panels",
    "alert_rules": r"alert rules with runbook link",
}


def _print_check(title: str, passed: bool, issues: list[str]) -> None:
    state = "PASS" if passed else "FAIL"
    print(f"[{state}] {title}")
    for issue in issues:
        print(f"  - {issue}")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _contains_pattern(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _extract_image_links(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)


def _find_evidence_images_by_item(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    issues: list[str] = []
    found: dict[str, str] = {}

    for key, pattern in REQUIRED_EVIDENCE_ITEMS.items():
        line_indexes = [idx for idx, line in enumerate(lines) if re.search(pattern, line, flags=re.IGNORECASE)]
        if not line_indexes:
            issues.append(f"Missing evidence item bullet: {key}")
            continue

        image_path: str | None = None
        for idx in line_indexes:
            for probe in range(idx, len(lines)):
                if probe > idx and re.match(r"^\s*-\s\[[ xX]\]\s", lines[probe]):
                    # Stop when next top-level checklist item begins.
                    break
                match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", lines[probe])
                if match:
                    image_path = match.group(1).strip()
                    break
            if image_path:
                break

        if image_path is None:
            issues.append(f"No screenshot linked for evidence item: {key}")
            continue

        found[key] = image_path

    return found, issues


def validate_dashboard_spec() -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not DASHBOARD_SPEC_PATH.exists():
        return False, [f"Missing file: {DASHBOARD_SPEC_PATH}"]

    text = DASHBOARD_SPEC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()

    for panel_name, pattern in REQUIRED_PANEL_PATTERNS.items():
        if not _contains_pattern(lowered, pattern):
            issues.append(f"Dashboard spec missing panel description: {panel_name}")

    if "threshold" not in lowered and "ngưỡng" not in lowered:
        issues.append("Dashboard spec missing threshold/SLO line note")

    # Units expected by rubric and dashboard quality bar.
    for unit in ("ms", "usd", "count"):
        if unit not in lowered:
            issues.append(f"Dashboard spec missing unit reference: {unit}")

    slo_cfg = _load_yaml(SLO_PATH)
    latency_obj = (
        slo_cfg.get("slis", {})
        .get("latency_p95_ms", {})
        .get("objective")
        if isinstance(slo_cfg.get("slis"), dict)
        else None
    )
    if latency_obj is not None:
        objective_text = f"{int(float(latency_obj))}ms"
        objective_text_spaced = f"{int(float(latency_obj))} ms"
        if objective_text not in lowered and objective_text_spaced not in lowered:
            issues.append(
                "Dashboard latency threshold is not aligned with config/slo.yaml "
                f"(expected mention of {objective_text})"
            )

    if not _contains_pattern(lowered, r"6\s*panels"):
        issues.append("Dashboard spec does not explicitly confirm 6 panels")

    return len(issues) == 0, issues


def validate_evidence_sheet() -> tuple[bool, list[str], list[str]]:
    issues: list[str] = []
    handover_items: list[str] = []

    if not EVIDENCE_PATH.exists():
        return False, [f"Missing file: {EVIDENCE_PATH}"], ["Prepare evidence sheet and screenshots"]

    text = EVIDENCE_PATH.read_text(encoding="utf-8")
    lowered = text.lower()

    for key, pattern in REQUIRED_EVIDENCE_ITEMS.items():
        if not _contains_pattern(lowered, pattern):
            issues.append(f"Evidence sheet missing required item text: {key}")
            handover_items.append(f"Capture and attach screenshot for {key}")

    image_map, item_issues = _find_evidence_images_by_item(text)
    issues.extend(item_issues)
    for msg in item_issues:
        if "No screenshot linked for evidence item:" in msg:
            item = msg.split(":", 1)[1].strip()
            handover_items.append(f"Attach screenshot evidence for {item}")

    base_dir = EVIDENCE_PATH.parent
    for key, rel_path in image_map.items():
        candidate = (base_dir / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)
        if not candidate.exists():
            issues.append(f"Evidence image file not found for {key}: {rel_path}")
            handover_items.append(f"Re-capture or fix broken image path for {key}")

    # If the sheet has images not attached to required bullets, still verify file paths are valid.
    for rel_path in _extract_image_links(text):
        candidate = (base_dir / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)
        if not candidate.exists():
            issues.append(f"Broken markdown image link: {rel_path}")

    return len(issues) == 0, issues, sorted(set(handover_items))


def validate_runtime(base_url: str, min_traffic: int) -> tuple[bool, list[str]]:
    issues: list[str] = []
    try:
        with httpx.Client(timeout=10.0) as client:
            def _fetch_metrics() -> dict[str, Any] | None:
                metrics_resp = client.get(f"{base_url}/metrics")
                if metrics_resp.status_code != 200:
                    issues.append(f"/metrics returned status {metrics_resp.status_code}")
                    return None
                payload = (
                    metrics_resp.json()
                    if metrics_resp.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                if not isinstance(payload, dict):
                    issues.append("/metrics did not return a JSON object")
                    return None
                return payload

            metrics = _fetch_metrics()
            if metrics is None:
                return False, issues

            required_metrics = [
                "traffic",
                "latency_p95",
                "error_rate_pct",
                "daily_cost_usd",
                "tokens_in_total",
                "tokens_out_total",
                "quality_avg",
            ]
            for metric_name in required_metrics:
                if metric_name not in metrics:
                    issues.append(f"/metrics missing key: {metric_name}")

            traffic = int(metrics.get("traffic", 0)) if str(metrics.get("traffic", "0")).isdigit() else 0
            if traffic < min_traffic:
                # Warm-up one request so dashboard runtime checks are stable after fresh restart.
                warmup_payload = {
                    "message": "Warmup request for member E validator.",
                    "user_id": "member_e_validator",
                    "feature": "qa",
                    "session_id": "member-e-runtime-check",
                }
                chat_resp = client.post(f"{base_url}/chat", json=warmup_payload)
                if chat_resp.status_code == 200:
                    metrics = _fetch_metrics() or metrics
                    traffic = int(metrics.get("traffic", 0)) if str(metrics.get("traffic", "0")).isdigit() else 0

            if traffic < min_traffic:
                issues.append(f"Traffic too low for dashboard evidence: {traffic} < {min_traffic}")

            for endpoint in ("/slo", "/alerts"):
                resp = client.get(f"{base_url}{endpoint}")
                if resp.status_code != 200:
                    issues.append(f"{endpoint} returned {resp.status_code}")

    except Exception as exc:
        issues.append(f"Runtime check failed: {exc}")

    return len(issues) == 0, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Member E deliverables (dashboard + evidence)")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL for runtime API checks")
    parser.add_argument("--check-runtime", action="store_true", help="Also validate runtime metric readiness")
    parser.add_argument("--min-traffic", type=int, default=1, help="Minimum traffic required for evidence readiness")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any check fails")
    args = parser.parse_args()

    dashboard_pass, dashboard_issues = validate_dashboard_spec()
    evidence_pass, evidence_issues, handover_items = validate_evidence_sheet()

    runtime_pass = True
    runtime_issues: list[str] = []
    if args.check_runtime:
        runtime_pass, runtime_issues = validate_runtime(args.base_url, args.min_traffic)

    print("=== Member E Validation ===")
    _print_check("Dashboard specification", dashboard_pass, dashboard_issues)
    _print_check("Evidence completeness", evidence_pass, evidence_issues)
    if args.check_runtime:
        _print_check("Runtime metric readiness", runtime_pass, runtime_issues)

    overall = dashboard_pass and evidence_pass and (runtime_pass if args.check_runtime else True)
    print(f"\nOverall: {'PASS' if overall else 'FAIL'}")

    if handover_items:
        print("\nRecommended handover to Member F:")
        for item in handover_items:
            print(f"- {item}")

    if args.strict and not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
