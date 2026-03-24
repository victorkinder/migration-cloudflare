from unittest.mock import Mock

import pytest

from app.cloudflare_client import get_account_id


def test_get_account_id_success(monkeypatch) -> None:
    def fake_get(url, headers, timeout):
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"result": [{"id": "acc-123"}]})
        return response

    monkeypatch.setattr("app.cloudflare_client.requests.get", fake_get)
    assert get_account_id("token") == "acc-123"


def test_get_account_id_no_accounts(monkeypatch) -> None:
    def fake_get(url, headers, timeout):
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"result": []})
        return response

    monkeypatch.setattr("app.cloudflare_client.requests.get", fake_get)
    with pytest.raises(ValueError, match="No Cloudflare account"):
        get_account_id("token")
