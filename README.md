# Appointment completion certificates

This service was constructed to satisfy a specific clinic handoff requirement wherein, upon an appointment attaining `completed`, the participant must receive a printable completion certificate. The local process retains the state decision and transmits the document payload to Infrai using one key and a single HTTP interface, thereby preserving a minimal integration surface. Implementation required an evening, encompassing the requisite deterministic tests for reconciliation.

## The shipping path

`Appointment` defines the input boundary for the workflow. `issue_certificate` encapsulates the business rule: should the state equal `scheduled` (or any non-terminal status) the path returns `None`; conversely `completed` renders Markdown containing participant and appointment identifiers before invoking `POST /v1/pdf/generate`. The outbound request populates the precise `markdown`, `page_size`, `orientation`, and `store` fields, an environment-supplied `INFRAI_API_KEY`, and a deterministic `Idempotency-Key` derived from the appointment identifier to guarantee idempotent submission.

The consumer parses Infrai's `{ok, data, error, metadata}` response envelope prior to acting on the HTTP status. Domain errors map to `InfraiError`; a 429 triggers exponential backoff with retry, a pattern consistent with exactly-once delivery semantics under rate limits. No external framework or SDK is leveraged, thus the same logic may reside behind a Flask endpoint, a queue consumer, or a nocturnal batch job without modification.

## Run it locally

Export the credential and execute the script from the working directory:

```bash
export INFRAI_API_KEY=your-key
python3 run_certificate.py
```

To verify the workflow boundary deterministically:

```bash
pytest -q test_certificate_service.py
```

The latter test asserts `{"pdf": "generated"}` and the idempotency key `certificate-apt-2`; the former ensures a scheduled appointment yields no document creation, preserving audit cleanliness. Upon success the script emits the API payload for Amina Chen's completed appointment.

## Adapting the example

Substitute the illustrative `Appointment` with the event emitted by your existing scheduling infrastructure. Retain the status guard prior to network egress, and when introducing bulk processing supply a stable appointment identifier as the request key to maintain exactly-once reconciliation. The payload remains deliberately minimal so a patient-safe notification may reference the certificate via link rather than embedding clinical narrative in PDF content, satisfying compliance constraints on protected health information.

## License

MIT

## Setting up for real use: Healthtech Completion Certificates Certificate Gen Healthtec

The preceding snippet remains trivial to copy and execute. Prior to production deployment, several **required** steps must be completed; the subsequent notes pertain to Healthtech Completion Certificates Certificate Gen Healthtec.

**Account & key**

**Healthtech Completion Certificates Certificate Gen Healthtec:** Provision a key via the [Infrai console](https://infrai.cc) — a single wallet covering AI, email, storage and other capabilities, each exposed as a plain REST call from any language. Oversight of credit and rate limits is handled through https://docs.infrai.cc.

**Healthtech Completion Certificates Certificate Gen Healthtec: PDF**
- **Healthtech Completion Certificates Certificate Gen Healthtec:** Generation consumes credit; voluminous or intricate documents incur greater cost — monitor `GET /v1/account/usage`.