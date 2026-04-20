from app.slo_alerts import evaluate_alerts, evaluate_slos


def test_evaluate_slos_pass_case() -> None:
    metrics = {
        "latency_p95": 2500,
        "error_rate_pct": 1.2,
        "daily_cost_usd": 1.8,
        "quality_avg": 0.82,
    }
    out = evaluate_slos(metrics)

    assert out["overall_status"] == "pass"
    assert out["slis"]["latency_p95_ms"]["status"] == "pass"
    assert out["slis"]["quality_score_avg"]["status"] == "pass"


def test_evaluate_slos_fail_case() -> None:
    metrics = {
        "latency_p95": 6400,
        "error_rate_pct": 8.0,
        "daily_cost_usd": 3.0,
        "quality_avg": 0.6,
    }
    out = evaluate_slos(metrics)

    assert out["overall_status"] == "fail"
    assert out["slis"]["latency_p95_ms"]["status"] == "fail"
    assert out["slis"]["error_rate_pct"]["status"] == "fail"


def test_evaluate_alerts_firing_on_absolute_thresholds() -> None:
    metrics = {
        "latency_p95_ms": 5500,
        "error_rate_pct": 7.5,
        "hourly_cost_usd": 0.1,
    }
    out = evaluate_alerts(metrics)

    firing_names = {a["name"] for a in out["alerts"] if a["status"] == "firing"}
    assert "high_latency_p95" in firing_names
    assert "high_error_rate" in firing_names


def test_evaluate_alerts_cost_spike_with_default_baseline() -> None:
    metrics = {
        "latency_p95_ms": 100,
        "error_rate_pct": 0.0,
        "hourly_cost_usd": 0.7,
    }
    out = evaluate_alerts(metrics)

    firing_names = {a["name"] for a in out["alerts"] if a["status"] == "firing"}
    assert "cost_budget_spike" in firing_names
