from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_QUERIES = Path("data/sample_queries.jsonl")


@dataclass
class RequestResult:
    status_code: int
    latency_ms: float
    correlation_id: str
    feature: str
    error: str | None = None


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil((p / 100) * len(ordered)) - 1))
    return ordered[rank]


def load_payloads(query_file: Path, repeat: int) -> list[dict]:
    lines = [line for line in query_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    payloads = [json.loads(line) for line in lines]
    return payloads * repeat


def send_request(base_url: str, timeout: float, payload: dict) -> RequestResult:
    feature = str(payload.get("feature", "unknown"))
    try:
        with httpx.Client(timeout=timeout) as client:
            start = time.perf_counter()
            response = client.post(f"{base_url}/chat", json=payload)
            latency_ms = (time.perf_counter() - start) * 1000
        body = response.json()
        correlation_id = str(body.get("correlation_id", "-"))
        return RequestResult(
            status_code=response.status_code,
            latency_ms=latency_ms,
            correlation_id=correlation_id,
            feature=feature,
            error=None if response.is_success else str(body.get("detail", "request_failed")),
        )
    except Exception as exc:
        return RequestResult(
            status_code=0,
            latency_ms=0.0,
            correlation_id="-",
            feature=feature,
            error=str(exc),
        )


def print_result(result: RequestResult) -> None:
    if result.error:
        print(
            f"[{result.status_code or 'ERR'}] {result.correlation_id} | "
            f"{result.feature} | {result.latency_ms:.1f}ms | {result.error}"
        )
        return
    print(f"[{result.status_code}] {result.correlation_id} | {result.feature} | {result.latency_ms:.1f}ms")


def print_summary(results: list[RequestResult], elapsed_s: float) -> None:
    latencies = [item.latency_ms for item in results if item.status_code == 200]
    failures = [item for item in results if item.status_code != 200]
    throughput = len(results) / elapsed_s if elapsed_s else 0.0

    print("\n--- Load Test Summary ---")
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(latencies)}")
    print(f"Failed: {len(failures)}")
    print(f"Elapsed time: {elapsed_s:.2f}s")
    print(f"Throughput: {throughput:.2f} req/s")

    if latencies:
        print(f"Latency avg: {statistics.mean(latencies):.1f}ms")
        print(f"Latency p50: {percentile(latencies, 50):.1f}ms")
        print(f"Latency p95: {percentile(latencies, 95):.1f}ms")
        print(f"Latency p99: {percentile(latencies, 99):.1f}ms")

    if failures:
        print("\n--- Failure Breakdown ---")
        counts: dict[str, int] = {}
        for item in failures:
            key = item.error or f"HTTP {item.status_code}"
            counts[key] = counts.get(key, 0) + 1
        for key, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])):
            print(f"{count}x {key}")


def fetch_metrics(base_url: str, timeout: float) -> None:
    try:
        response = httpx.get(f"{base_url}/metrics", timeout=timeout)
        response.raise_for_status()
    except Exception as exc:
        print(f"\nCould not fetch /metrics: {exc}")
        return

    print("\n--- App Metrics Snapshot ---")
    metrics = response.json()
    for key, value in metrics.items():
        print(f"{key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send sample chat requests and summarize latency/error signals.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Target app base URL")
    parser.add_argument("--query-file", type=Path, default=DEFAULT_QUERIES, help="JSONL file with chat payloads")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of parallel requests")
    parser.add_argument("--repeat", type=int, default=1, help="Replay the query file N times")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout in seconds")
    parser.add_argument("--skip-metrics", action="store_true", help="Do not fetch /metrics after the run")
    args = parser.parse_args()

    payloads = load_payloads(args.query_file, max(1, args.repeat))

    started = time.perf_counter()
    if args.concurrency > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = [
                executor.submit(send_request, args.base_url, args.timeout, payload)
                for payload in payloads
            ]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
    else:
        results = [send_request(args.base_url, args.timeout, payload) for payload in payloads]
    elapsed_s = time.perf_counter() - started

    for result in results:
        print_result(result)

    print_summary(results, elapsed_s)

    if not args.skip_metrics:
        fetch_metrics(args.base_url, args.timeout)


if __name__ == "__main__":
    main()
