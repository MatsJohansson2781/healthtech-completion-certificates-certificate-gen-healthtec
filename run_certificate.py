import json

from certificate_service import Appointment, InfraiClient, issue_certificate


def main() -> None:
    appointment = Appointment("Amina Chen", "apt-2048", "completed", "2026-09-09")
    result = issue_certificate(appointment, InfraiClient())
    print(json.dumps({"appointment_id": appointment.appointment_id, "certificate": result}, indent=2))


if __name__ == "__main__":
    main()
