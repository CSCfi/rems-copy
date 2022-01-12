"""Localisation checker."""
import sys

import requests


def get_languages(c, env):
    """Get languages supported by env."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + "/api/config", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_languages({env}), {e}")

    if response.status_code == 200:
        return response.json()["languages"]
    else:
        sys.exit(f"ABORT: get_languages({env}) responded with {str(response.status_code)}")
