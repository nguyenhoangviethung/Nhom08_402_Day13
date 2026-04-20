from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Allow running this script directly from the scripts/ folder context.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.pii import scrub_text


LOG_PATH = Path("data/logs.jsonl")


def _sanitize_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    return {k: scrub_text(v) if isinstance(v, str) else v for k, v in payload.items()}


def normalize_record(record: dict[str, Any], line_index: int) -> dict[str, Any]:
    normalized = dict(record)

    normalized.setdefault("service", "app")
    normalized.setdefault("env", "dev")
    if isinstance(normalized.get("event"), str):
        normalized["event"] = scrub_text(normalized["event"])

    correlation_id = normalized.get("correlation_id") or normalized.get("request_id")
    if not correlation_id:
        if normalized.get("service") == "api":
            correlation_id = f"legacy-{line_index:04d}"
        else:
            correlation_id = "system"
    normalized["correlation_id"] = str(correlation_id)

    normalized["payload"] = _sanitize_payload(normalized.get("payload"))

    if normalized.get("service") == "api":
        seed = normalized["correlation_id"]
        normalized.setdefault("feature", "legacy-feature")
        normalized.setdefault("model", "unknown-model")
        normalized.setdefault("session_id", f"legacy-session-{seed[-8:]}")
        normalized.setdefault("user_id_hash", hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12])

    return normalized


def main() -> None:
    if not LOG_PATH.exists():
        raise SystemExit(f"{LOG_PATH} does not exist")

    normalized_lines: list[str] = []
    rewritten = 0
    skipped = 0

    for idx, raw in enumerate(LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            skipped += 1
            continue

        fixed = normalize_record(rec, idx)
        if fixed != rec:
            rewritten += 1
        normalized_lines.append(json.dumps(fixed, ensure_ascii=False))

    LOG_PATH.write_text("\n".join(normalized_lines) + "\n", encoding="utf-8")
    print(
        f"Normalized {len(normalized_lines)} records. "
        f"Rewritten: {rewritten}. Skipped invalid lines: {skipped}."
    )


if __name__ == "__main__":
    main()
