#!/usr/bin/env python3
"""PrusaLink Dual-Purpose Bot Bridge for Raspberry Pi 4.

Listens to local PrusaLink webhooks or periodically polls the local PrusaLink API
(running on the same Pi on port 80/8080) and sends Telegram photo alerts with print progress
and completion notifications (e.g. "Print terminat cu succes! Patul se răcește").
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from src.notifier import (
    fetch_prusalink_snapshot,
    fetch_prusalink_status,
    send_prusalink_alert,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (prusalink_bridge) %(message)s",
)
log = logging.getLogger("olx.prusalink")


class PrusaWebhookHandler(BaseHTTPRequestHandler):
    """Lightweight HTTP server handler that receives JSON webhook POSTs from PrusaLink/Prusa Connect."""

    prusalink_host: str = "http://127.0.0.1:8080"
    api_key: Optional[str] = None

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        event_type = payload.get("event") or payload.get("state") or "PRINTING"
        job = payload.get("job") if isinstance(payload, dict) else {}
        if not isinstance(job, dict):
            job = {}
        file_info = job.get("file") if isinstance(job, dict) else None
        filename = file_info.get("display_name", "") if isinstance(file_info, dict) else ""
        progress = job.get("progress") if isinstance(job, dict) else None
        time_rem = job.get("time_remaining") if isinstance(job, dict) else None

        printer = payload.get("printer") if isinstance(payload, dict) else {}
        if not isinstance(printer, dict):
            printer = {}
        telemetry = printer.get("telemetry") if isinstance(printer, dict) else None
        nozzle = telemetry.get("temp_nozzle") if isinstance(telemetry, dict) else None
        bed = telemetry.get("temp_bed") if isinstance(telemetry, dict) else None

        details = {
            "filename": filename,
            "progress_pct": progress,
            "nozzle_temp": nozzle,
            "bed_temp": bed,
            "time_remaining": time_rem,
        }

        # Attempt to grab webcam snapshot from local PrusaLink
        photo_bytes = fetch_prusalink_snapshot(self.prusalink_host, api_key=self.api_key)

        log.info("Received PrusaLink webhook event: %s (file: %s)", event_type, filename)
        send_prusalink_alert(event_type, details, photo_bytes=photo_bytes)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def log_message(self, format: str, *args: object) -> None:
        pass


def run_poller_loop(
    prusalink_host: str = "http://127.0.0.1:8080",
    api_key: Optional[str] = None,
    poll_interval: int = 15,
) -> None:
    """Continuously polls local PrusaLink API and dispatches alerts on state transitions."""
    log.info("Starting PrusaLink poller against %s (interval: %ds)...", prusalink_host, poll_interval)
    last_state: Optional[str] = None
    last_milestone = -1

    while True:
        try:
            status_data = fetch_prusalink_status(prusalink_host, api_key=api_key)
            if status_data and isinstance(status_data, dict):
                printer = status_data.get("printer")
                if not isinstance(printer, dict):
                    printer = {}
                state = str(printer.get("state", "IDLE") or "IDLE").upper()
                job = status_data.get("job")
                if not isinstance(job, dict):
                    job = {}
                progress = job.get("progress") or 0.0
                telemetry = printer.get("telemetry")
                nozzle = telemetry.get("temp_nozzle") if isinstance(telemetry, dict) else None
                bed = telemetry.get("temp_bed") if isinstance(telemetry, dict) else None
                file_info = job.get("file")
                filename = file_info.get("display_name", "") if isinstance(file_info, dict) else ""
                time_rem = job.get("time_remaining")

                details = {
                    "filename": filename,
                    "progress_pct": progress,
                    "nozzle_temp": nozzle,
                    "bed_temp": bed,
                    "time_remaining": time_rem,
                }

                # Transition into finished
                if state in ("FINISHED", "COMPLETED") and last_state != state:
                    log.info("Print finished detected! Sending Telegram alert with snapshot...")
                    photo_bytes = fetch_prusalink_snapshot(prusalink_host, api_key=api_key)
                    send_prusalink_alert("FINISHED", details, photo_bytes=photo_bytes)
                    last_milestone = -1

                # Progress milestones (e.g. 50%)
                elif state == "PRINTING":
                    current_milestone = int(progress // 25) * 25
                    if current_milestone > last_milestone and current_milestone in (25, 50, 75):
                        log.info("Print reached %d%% milestone! Sending Telegram alert...", current_milestone)
                        photo_bytes = fetch_prusalink_snapshot(prusalink_host, api_key=api_key)
                        send_prusalink_alert("PRINTING", details, photo_bytes=photo_bytes)
                        last_milestone = current_milestone

                last_state = state
        except Exception as e:
            log.debug("PrusaLink poll iteration error: %s", e)

        time.sleep(poll_interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="PrusaLink Telegram Notifier Bridge for Raspberry Pi 4")
    parser.add_argument("--mode", choices=["poll", "webhook"], default="poll", help="Mode: poll API or listen for webhooks")
    parser.add_argument("--host", default=os.getenv("PRUSALINK_HOST", "http://127.0.0.1:8080"), help="PrusaLink host URL")
    parser.add_argument("--api-key", default=os.getenv("PRUSALINK_API_KEY"), help="PrusaLink API key (optional)")
    parser.add_argument("--webhook-port", type=int, default=8088, help="Port to listen for incoming webhooks")
    parser.add_argument("--interval", type=int, default=15, help="Poll interval in seconds")

    args = parser.parse_args()

    if args.mode == "webhook":
        PrusaWebhookHandler.prusalink_host = args.host
        PrusaWebhookHandler.api_key = args.api_key
        server = HTTPServer(("0.0.0.0", args.webhook_port), PrusaWebhookHandler)
        log.info("Listening for PrusaLink webhooks on port %d...", args.webhook_port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
    else:
        run_poller_loop(
            prusalink_host=args.host,
            api_key=args.api_key,
            poll_interval=args.interval,
        )


if __name__ == "__main__":
    main()
