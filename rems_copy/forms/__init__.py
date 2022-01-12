"""Form operations."""
import sys

import requests


def copy_forms(config, source, destination):
    """Copy forms from source to destination if name doesn't already exist in destination."""
    source_forms = get_forms(config, source)
    destination_forms = get_forms(config, destination)
    destination_form_names = [df["form/title"] for df in destination_forms]

    skipped = []
    created = []

    for i, sf in enumerate(source_forms):
        sys.stdout.write(f"\rcopying forms {i+1}/{len(source_forms)}")
        sys.stdout.flush()
        if sf["form/title"] not in destination_form_names:
            form_data = download_form(config, source, sf["form/id"])
            post_form(config, form_data, destination)
            created.append(sf["form/title"])
        else:
            skipped.append(sf["form/title"])

    print(f"\nskipped forms that already exist at {destination}: {skipped}")
    print(f"created new forms at {destination}: {created}")


def download_form(c, env, identifier):
    """Download form data."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + "/api/forms/" + str(identifier), headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: download_form({env}, {str(identifier)}), {e}")

    if response.status_code == 200:
        form = response.json()
        # remove forbidden keys
        del form["form/id"]
        del form["organization"]["organization/short-name"]
        del form["organization"]["organization/name"]
        del form["form/errors"]
        del form["enabled"]
        del form["archived"]
        return form
    else:
        sys.exit(f"ABORT: download_form({env}, {str(identifier)}) responded with {str(response.status_code)}")


def post_form(c, form, env):
    """Post form to environment."""
    form["organization"]["organization/id"] = c[env]["organisation"]
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/forms/create", headers=headers, json=form)
    except Exception as e:
        sys.exit(f"ERROR: post_form(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_form() responded with {str(response.status_code)}, {response.text}")


def get_forms(c, env):
    """Get available forms."""
    print(f"downloading forms from {env}")
    params = {
        "disabled": "false",
        "archived": "false",
    }
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + "/api/forms", headers=headers, params=params)
    except Exception as e:
        sys.exit(f"ERROR: get_forms({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_forms({env}) responded with {str(response.status_code)}")


def get_form(c, env, form_id):
    """Get specific form."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + f"/api/forms/{form_id}", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_form({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_form({env}) responded with {str(response.status_code)}")
