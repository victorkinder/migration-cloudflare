from __future__ import annotations

import requests


def get_account_id(cloudflare_token: str) -> str:
    headers = {
        "Authorization": f"Bearer {cloudflare_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        "https://api.cloudflare.com/client/v4/accounts",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    accounts = payload.get("result", [])
    if not accounts:
        raise ValueError("No Cloudflare account found for the provided token.")

    account_id = accounts[0].get("id", "").strip()
    if not account_id:
        raise ValueError("Cloudflare account id is missing in API response.")
    return account_id
