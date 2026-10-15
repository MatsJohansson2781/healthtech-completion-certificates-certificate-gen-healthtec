from certificate_service import Appointment, issue_certificate


class FakeClient:
    def __init__(self):
        self.calls = []

    def generate_pdf(self, markdown, request_id):
        self.calls.append((markdown, request_id))
        return {"pdf": "generated"}


def test_pending_appointment_does_not_issue_certificate():
    client = FakeClient()
    result = issue_certificate(Appointment("Lee", "apt-1", "scheduled"), client)
    assert result is None
    assert client.calls == []


def test_completed_appointment_issues_once_with_stable_key():
    client = FakeClient()
    result = issue_certificate(Appointment("Lee", "apt-2", "completed", "2026-09-09"), client)
    assert result == {"pdf": "generated"}
    assert client.calls[0][1] == "certificate-apt-2"
