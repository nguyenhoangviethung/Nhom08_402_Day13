from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


LOG_PATH = Path("data/logs.jsonl")
BLUEPRINT_PATH = Path("docs/blueprint-template.md")
MEMBER_D_VALIDATOR_PATH = Path("scripts/validate_member_d.py")
MEMBER_E_VALIDATOR_PATH = Path("scripts/validate_member_e.py")

ENRICHMENT_FIELDS = {"user_id_hash", "session_id", "feature", "model"}

KNOWN_PLACEHOLDERS = {
    "[GROUP_NAME]",
    "[REPO_URL]",
    "[MEMBERS]",
    "[VALIDATE_LOGS_FINAL_SCORE]",
    "[TOTAL_TRACES_COUNT]",
    "[PII_LEAKS_FOUND]",
    "[EVIDENCE_CORRELATION_ID_SCREENSHOT]",
    "[EVIDENCE_PII_REDACTION_SCREENSHOT]",
    "[EVIDENCE_TRACE_WATERFALL_SCREENSHOT]",
    "[TRACE_WATERFALL_EXPLANATION]",
    "[DASHBOARD_6_PANELS_SCREENSHOT]",
    "[SLO_TABLE]",
    "[ALERT_RULES_SCREENSHOT]",
    "[SAMPLE_RUNBOOK_LINK]",
    "[SCENARIO_NAME]",
    "[SYMPTOMS_OBSERVED]",
    "[ROOT_CAUSE_PROVED_BY]",
    "[FIX_ACTION]",
    "[PREVENTIVE_MEASURE]",
    "[TASKS_COMPLETED]",
    "[EVIDENCE_LINK]",
    "[BONUS_COST_OPTIMIZATION]",
    "[BONUS_AUDIT_LOGS]",
    "[BONUS_CUSTOM_METRIC]",
}


def _extract_json_blob(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def compute_log_score(log_path: Path) -> dict[str, Any]:
    if not log_path.exists():
        return {
            "score": 0,
            "total": 0,
            "missing_required": -1,
            "missing_enrichment": -1,
            "correlation_count": 0,
            "pii_hits": -1,
            "error": f"{log_path} not found",
        }

    records: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not records:
        return {
            "score": 0,
            "total": 0,
            "missing_required": -1,
            "missing_enrichment": -1,
            "correlation_count": 0,
            "pii_hits": -1,
            "error": "No valid JSON records",
        }

    missing_required = 0
    missing_enrichment = 0
    pii_hits = 0
    correlation_ids = set()

    for rec in records:
        if not {"ts", "level", "event"}.issubset(rec.keys()):
            missing_required += 1

        if rec.get("service") == "api":
            if "correlation_id" not in rec or rec.get("correlation_id") == "MISSING":
                missing_required += 1
            if not ENRICHMENT_FIELDS.issubset(rec.keys()):
                missing_enrichment += 1

        raw = json.dumps(rec, ensure_ascii=False)
        if "@" in raw or "4111" in raw:
            pii_hits += 1

        cid = rec.get("correlation_id")
        if cid and cid != "MISSING":
            correlation_ids.add(cid)

    score = 100
    if missing_required > 0:
        score -= 30
    if len(correlation_ids) < 2:
        score -= 20
    if missing_enrichment > 0:
        score -= 20
    if pii_hits > 0:
        score -= 30

    return {
        "score": max(0, score),
        "total": len(records),
        "missing_required": missing_required,
        "missing_enrichment": missing_enrichment,
        "correlation_count": len(correlation_ids),
        "pii_hits": pii_hits,
        "error": None,
    }


def get_trace_count() -> tuple[int | None, str | None]:
    cmd = ["npx", "-y", "langfuse-cli", "api", "traces", "list", "--limit", "1"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
    except FileNotFoundError:
        return None, "npx not found"
    except subprocess.TimeoutExpired:
        return None, "langfuse-cli timeout"

    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        return None, f"langfuse-cli failed: {stderr}"

    payload = _extract_json_blob(proc.stdout)
    if not payload:
        return None, "cannot parse JSON from langfuse-cli output"

    total_items = payload.get("meta", {}).get("totalItems")
    if isinstance(total_items, int):
        return total_items, None

    return None, "missing meta.totalItems in langfuse response"


def find_blueprint_placeholders(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing_file:{path}"]

    text = path.read_text(encoding="utf-8")
    unresolved = {token for token in KNOWN_PLACEHOLDERS if token in text}

    generic_matches = set(re.findall(r"\[(?:MEMBER_[A-Z0-9_]+_NAME|Name|Path to image)\]", text))
    unresolved |= generic_matches

    return sorted(unresolved)


def write_group_metrics(
    path: Path,
    validate_score: int,
    trace_count: int | None,
    pii_leaks: int,
) -> bool:
    if not path.exists():
        return False

    text = path.read_text(encoding="utf-8")
    traces = trace_count if trace_count is not None else "N/A"

    updates = {
        r"^- \[VALIDATE_LOGS_FINAL_SCORE\]:.*$": f"- [VALIDATE_LOGS_FINAL_SCORE]: {validate_score}/100",
        r"^- \[TOTAL_TRACES_COUNT\]:.*$": f"- [TOTAL_TRACES_COUNT]: {traces}",
        r"^- \[PII_LEAKS_FOUND\]:.*$": f"- [PII_LEAKS_FOUND]: {pii_leaks}",
    }

    new_text = text
    for pattern, replacement in updates.items():
        new_text = re.sub(pattern, replacement, new_text, flags=re.MULTILINE)

    if new_text == text:
        return False

    path.write_text(new_text, encoding="utf-8")
    return True


def run_member_validator(script_path: Path, *, check_runtime: bool) -> tuple[bool, list[str]]:
    if not script_path.exists():
        return False, [f"missing validator script: {script_path}"]

    cmd = [sys.executable, str(script_path), "--strict"]
    if check_runtime:
        cmd.append("--check-runtime")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180)
    except subprocess.TimeoutExpired:
        return False, [f"validator timeout: {script_path}"]

    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    issues = [line.strip()[2:].strip() for line in output.splitlines() if line.strip().startswith("-")]

    if proc.returncode == 0:
        return True, []

    if not issues:
        summary = output.strip().splitlines()[-1] if output.strip() else "validator failed without details"
        issues = [summary]
    return False, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Member F pre-demo quality gate")
    parser.add_argument("--min-log-score", type=int, default=80, help="Minimum acceptable validate logs score")
    parser.add_argument("--min-traces", type=int, default=10, help="Minimum required Langfuse traces")
    parser.add_argument(
        "--check-member-de-runtime",
        action="store_true",
        help="Run Member D/E runtime checks in addition to static checks",
    )
    parser.add_argument(
        "--skip-member-de-checks",
        action="store_true",
        help="Skip Member D/E validator checks",
    )
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code if any check fails")
    parser.add_argument(
        "--write-group-metrics",
        action="store_true",
        help="Write validate score, total traces, and pii leaks into docs/blueprint-template.md",
    )
    args = parser.parse_args()

    load_dotenv()

    log_metrics = compute_log_score(LOG_PATH)
    trace_count, trace_error = get_trace_count()
    unresolved = find_blueprint_placeholders(BLUEPRINT_PATH)

    member_d_pass = True
    member_e_pass = True
    member_d_issues: list[str] = []
    member_e_issues: list[str] = []

    if not args.skip_member_de_checks:
        member_d_pass, member_d_issues = run_member_validator(
            MEMBER_D_VALIDATOR_PATH,
            check_runtime=args.check_member_de_runtime,
        )
        member_e_pass, member_e_issues = run_member_validator(
            MEMBER_E_VALIDATOR_PATH,
            check_runtime=args.check_member_de_runtime,
        )

    log_pass = bool(log_metrics["error"] is None and log_metrics["score"] >= args.min_log_score)
    trace_pass = bool(trace_error is None and trace_count is not None and trace_count >= args.min_traces)
    blueprint_pass = len(unresolved) == 0

    print("=== Member F Demo Gate ===")
    print(
        f"[{'PASS' if log_pass else 'FAIL'}] Logs: score={log_metrics['score']}/100 "
        f"(missing_required={log_metrics['missing_required']}, "
        f"missing_enrichment={log_metrics['missing_enrichment']}, "
        f"pii_hits={log_metrics['pii_hits']}, correlation_ids={log_metrics['correlation_count']})"
    )
    if log_metrics["error"]:
        print(f"  Error: {log_metrics['error']}")

    if trace_error:
        print(f"[FAIL] Traces: {trace_error}")
    else:
        print(f"[{'PASS' if trace_pass else 'FAIL'}] Traces: total={trace_count} (required>={args.min_traces})")

    print(f"[{'PASS' if blueprint_pass else 'FAIL'}] Blueprint placeholders unresolved: {len(unresolved)}")
    if unresolved:
        preview = ", ".join(unresolved[:8])
        print(f"  First unresolved: {preview}")

    if args.skip_member_de_checks:
        print("[SKIP] Member D/E validators: skipped by flag")
    else:
        print(f"[{'PASS' if member_d_pass else 'FAIL'}] Member D validator")
        for issue in member_d_issues[:5]:
            print(f"  - {issue}")

        print(f"[{'PASS' if member_e_pass else 'FAIL'}] Member E validator")
        for issue in member_e_issues[:5]:
            print(f"  - {issue}")

    handover_items: list[str] = []
    if not member_d_pass:
        handover_items.append("Member D backlog: run load test + incident evidence capture and update report")
    if not member_e_pass:
        handover_items.append("Member E backlog: complete dashboard/evidence screenshots and update report")

    if handover_items:
        print("\n[ACTION] Assign handover to Member F:")
        for item in handover_items:
            print(f"- {item}")
        print("Member F should record these takeover tasks in docs/blueprint-template.md")

    overall_pass = log_pass and trace_pass and blueprint_pass and member_d_pass and member_e_pass
    print(f"\nOverall: {'PASS' if overall_pass else 'FAIL'}")

    if args.write_group_metrics:
        written = write_group_metrics(
            BLUEPRINT_PATH,
            validate_score=log_metrics["score"],
            trace_count=trace_count,
            pii_leaks=log_metrics["pii_hits"],
        )
        if written:
            print("Updated group metrics in docs/blueprint-template.md")
        else:
            print("No blueprint update performed")

    if args.strict and not overall_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
