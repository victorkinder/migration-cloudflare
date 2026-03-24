from unittest.mock import Mock

from app.notifier import send_migration_data


def test_send_migration_data_posts_correct_payload(monkeypatch) -> None:
    sent = {}

    def fake_post(url, json, timeout):
        sent["url"] = url
        sent["json"] = json
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"success": True, "persistedFiles": 2})
        return response

    monkeypatch.setattr("app.notifier.requests.post", fake_post)

    result = send_migration_data(
        email="user@example.com",
        project_name="domain-com",
        files={"/index.html": "<h1>ok</h1>"},
        migration_url="https://example.com/migrateCloudflareProject",
        migration_key="secret-key",
    )

    assert sent["url"] == "https://example.com/migrateCloudflareProject"
    assert sent["json"]["migration_key"] == "secret-key"
    assert sent["json"]["email"] == "user@example.com"
    assert sent["json"]["projectName"] == "domain-com"
    assert sent["json"]["files"] == {"/index.html": "<h1>ok</h1>"}
    assert result["success"] is True
