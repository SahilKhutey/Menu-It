#!/usr/bin/env python3
"""Post-deployment smoke testing verification script (FCD-12 WP-16)."""

import asyncio
import os
import sys
import time

import httpx

TIMEOUT_SECONDS = 15.0


async def _run_smoke_async(in_process: bool) -> bool:
    base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

    if in_process:
        print("[SMOKE] Running post-deployment smoke verification in-process via ASGITransport")  # noqa: T201
        api_src = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api", "src")
        )
        if api_src not in sys.path:
            sys.path.insert(0, api_src)
        from menu_it.application import create_application

        app = create_application()
        client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        )
    else:
        print(f"[SMOKE] Running post-deployment smoke verification against: {base_url}")  # noqa: T201
        client = httpx.AsyncClient(timeout=TIMEOUT_SECONDS, base_url=base_url)

    endpoints = [
        ("/api/v1/health", [200], "API Liveness & Health"),
        ("/api/v1/database/health", [200, 503], "Database Connectivity Probe"),
        ("/api/v1/system/info", [200], "System Information"),
        ("/api/v1/metrics", [200], "Telemetry Metrics"),
    ]

    all_passed = True

    async with client:
        for path, expected_statuses, description in endpoints:
            start_time = time.time()
            try:
                resp = await client.get(path)
                duration_ms = (time.time() - start_time) * 1000
                if resp.status_code in expected_statuses:
                    print(  # noqa: T201
                        f"  [PASS] {description} ({path}): status={resp.status_code} in {duration_ms:.1f}ms"
                    )
                else:
                    print(  # noqa: T201
                        f"  [FAIL] {description} ({path}): expected status in {expected_statuses}, "
                        f"got {resp.status_code} in {duration_ms:.1f}ms",
                        file=sys.stderr,
                    )
                    all_passed = False
            except Exception as exc:
                print(  # noqa: T201
                    f"  [FAIL] {description} ({path}): connection error: {exc}",
                    file=sys.stderr,
                )
                all_passed = False

    return all_passed


def run_smoke_tests() -> bool:
    in_process = os.environ.get("SMOKE_IN_PROCESS") == "1" or "--in-process" in sys.argv
    return asyncio.run(_run_smoke_async(in_process))


if __name__ == "__main__":
    success = run_smoke_tests()
    if not success:
        print("[SMOKE] Post-deployment smoke tests FAILED.", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    print("[SMOKE] Post-deployment smoke tests PASSED successfully.")  # noqa: T201
    sys.exit(0)
