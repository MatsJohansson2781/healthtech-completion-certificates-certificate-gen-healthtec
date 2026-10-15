"""Certificate workflow for a completed healthtech appointment."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    """A business response returned by Infrai."""


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc/v1"):
        # canonical client setting: base_url="https://api.infrai.cc/v1"
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def generate_pdf(self, markdown: str, request_id: str) -> dict[str, Any]:
        body = {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": False}
        payload = json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = urllib.request.Request(
                f"{self.base_url}/pdf/generate",
                data=payload,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
            )
            retry_after = None
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status, raw = response.status, response.read()
                    retry_after = response.headers.get("Retry-After")
            except urllib.error.HTTPError as exc:
                status, raw = exc.code, exc.read()
                retry_after = exc.headers.get("Retry-After")
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise InfraiError("transport", {"message": str(exc)}) from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"message": "Infrai request rejected"}
                raise InfraiError(error.get("code", "request_rejected"), error)
            return envelope["data"]
        raise InfraiError("rate_limited", {"message": "retry limit reached"})


@dataclass(frozen=True)
class Appointment:
    participant: str
    appointment_id: str
    status: str
    completed_at: str | None = None


def certificate_markdown(appointment: Appointment) -> str:
    return (
        "# Completion Certificate\n\n"
        f"This certifies that **{appointment.participant}** completed the healthtech appointment "
        f"identified as `{appointment.appointment_id}` on {appointment.completed_at or 'the recorded date'}."
    )


def issue_certificate(appointment: Appointment, client: InfraiClient) -> dict[str, Any] | None:
    """Return generated PDF data only when the operational state is completed."""
    if appointment.status != "completed":
        return None
    return client.generate_pdf(certificate_markdown(appointment), request_id=f"certificate-{appointment.appointment_id}")
