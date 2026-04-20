from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

SLO_CONFIG_PATH = Path("config/slo.yaml")
ALERT_RULES_PATH = Path("config/alert_rules.yaml")

METRIC_ALIASES: dict[str, tuple[str, ...]] = {
    # SLO/alert configs often use explicit unit suffixes, while runtime metrics can be shorter.
    "latency_p95_ms": ("latency_p95_ms", "latency_p95"),
    "latency_p95": ("latency_p95", "latency_p95_ms"),
    "quality_score_avg": ("quality_score_avg", "quality_avg"),
    "quality_avg": ("quality_avg", "quality_score_avg"),
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _resolve_metric_value(metric_name: str, metrics: dict[str, Any]) -> tuple[float, str]:
    for candidate in METRIC_ALIASES.get(metric_name, (metric_name,)):
        if candidate in metrics:
            return _as_float(metrics.get(candidate, 0.0)), candidate
    return _as_float(metrics.get(metric_name, 0.0)), metric_name


def evaluate_slos(metrics: dict[str, Any], config_path: Path = SLO_CONFIG_PATH) -> dict[str, Any]:
    config = _load_yaml(config_path)
    slis = config.get("slis", {}) if isinstance(config.get("slis", {}), dict) else {}

    mapping = {
        "latency_p95_ms": "latency_p95",
        "error_rate_pct": "error_rate_pct",
        "daily_cost_usd": "daily_cost_usd",
        "quality_score_avg": "quality_avg",
    }

    evaluated: dict[str, Any] = {}
    for sli_name, spec in slis.items():
        if not isinstance(spec, dict):
            continue
        metric_key = mapping.get(sli_name, sli_name)
        current_value, resolved_metric_key = _resolve_metric_value(metric_key, metrics)
        objective = _as_float(spec.get("objective", 0.0))

        # Lower-is-better for latency, error, and cost. Higher-is-better for quality.
        comparator = "<=" if sli_name in {"latency_p95_ms", "error_rate_pct", "daily_cost_usd"} else ">="
        passed = current_value <= objective if comparator == "<=" else current_value >= objective

        evaluated[sli_name] = {
            "metric_key": metric_key,
            "resolved_metric_key": resolved_metric_key,
            "objective": objective,
            "target": _as_float(spec.get("target", 0.0)),
            "window": config.get("window", "unknown"),
            "current": round(current_value, 4),
            "comparator": comparator,
            "status": "pass" if passed else "fail",
            "note": spec.get("note"),
        }

    service_level = "pass" if evaluated and all(v.get("status") == "pass" for v in evaluated.values()) else "fail"
    return {
        "service": config.get("service", "day13-observability-lab"),
        "window": config.get("window", "unknown"),
        "overall_status": service_level,
        "slis": evaluated,
    }


def _evaluate_condition(condition: str, metrics: dict[str, Any]) -> tuple[bool, str]:
    # Example: latency_p95_ms > 5000 for 30m
    absolute_pattern = re.compile(
        r"^(?P<metric>[a-zA-Z0-9_]+)\s*(?P<op>>=|<=|>|<|==)\s*(?P<threshold>[0-9]+(?:\.[0-9]+)?)\s+for\s+(?P<window>[0-9]+[mh])$"
    )
    match = absolute_pattern.match(condition.strip())
    if match:
        metric = match.group("metric")
        op = match.group("op")
        threshold = float(match.group("threshold"))
        value, resolved_metric = _resolve_metric_value(metric, metrics)

        operations = {
            ">": value > threshold,
            "<": value < threshold,
            ">=": value >= threshold,
            "<=": value <= threshold,
            "==": value == threshold,
        }
        evidence_metric = resolved_metric if resolved_metric != metric else metric
        return (
            operations.get(op, False),
            f"{evidence_metric}={round(value, 4)}, threshold={threshold}, window={match.group('window')}",
        )

    # Example: hourly_cost_usd > 2x_baseline for 15m
    baseline_pattern = re.compile(
        r"^(?P<metric>[a-zA-Z0-9_]+)\s*>\s*(?P<factor>[0-9]+(?:\.[0-9]+)?)x_baseline\s+for\s+(?P<window>[0-9]+[mh])$"
    )
    match = baseline_pattern.match(condition.strip())
    if match:
        metric = match.group("metric")
        factor = float(match.group("factor"))
        baseline = _as_float(os.getenv("COST_BASELINE_HOURLY_USD", "0.25"), default=0.25)
        threshold = baseline * factor
        value, resolved_metric = _resolve_metric_value(metric, metrics)
        evidence_metric = resolved_metric if resolved_metric != metric else metric
        return value > threshold, (
            f"{evidence_metric}={round(value, 4)}, baseline={baseline}, factor={factor}, threshold={round(threshold, 4)}, "
            f"window={match.group('window')}"
        )

    return False, "condition_not_supported"


def evaluate_alerts(metrics: dict[str, Any], config_path: Path = ALERT_RULES_PATH) -> dict[str, Any]:
    config = _load_yaml(config_path)
    alerts = config.get("alerts", []) if isinstance(config.get("alerts", []), list) else []

    evaluated_alerts: list[dict[str, Any]] = []
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        condition = str(alert.get("condition", "")).strip()
        is_firing, evidence = _evaluate_condition(condition, metrics)

        evaluated_alerts.append(
            {
                "name": alert.get("name", "unknown"),
                "severity": alert.get("severity", "P3"),
                "owner": alert.get("owner", "unknown"),
                "type": alert.get("type", "symptom-based"),
                "condition": condition,
                "runbook": alert.get("runbook"),
                "status": "firing" if is_firing else "ok",
                "evidence": evidence,
            }
        )

    firing = [a for a in evaluated_alerts if a.get("status") == "firing"]
    return {
        "total": len(evaluated_alerts),
        "firing": len(firing),
        "alerts": evaluated_alerts,
    }
