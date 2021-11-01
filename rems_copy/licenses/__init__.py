"""License operations."""
import sys

import requests


def copy_licenses(config, source, destination):
    """Copy licenses from source to destination if name doesn't already exist in destination."""
    source_licenses = get_licenses(config, source)
    destination_licenses = get_licenses(config, destination)
    destination_license_names = [dl["localizations"][config["language"]]["title"] for dl in destination_licenses]

    skipped = []
    created = []
    not_supported = []
    for i, sl in enumerate(source_licenses):
        # attachment licenses are more complicated and are not supported as of yet
        if sl["licensetype"] == "attachment":
            not_supported.append(source_licenses.pop(i))

    for i, sl in enumerate(source_licenses):
        sys.stdout.write(f"\rcopying licenses {i+1}/{len(source_licenses)}")
        sys.stdout.flush()
        if sl["localizations"][config["language"]]["title"] not in destination_license_names:
            license_data = download_license(config, source, sl["id"])
            post_license(config, license_data, destination)
            created.append(sl["localizations"][config["language"]]["title"])
        else:
            skipped.append(sl["localizations"][config["language"]]["title"])

    print(f"\nskipped licenses that already exist at {destination}: {skipped}")
    print(f"\ncreated new licenses at {destination}: {created}")


def download_license(c, env, identifier):
    """Download license data."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + "/api/licenses/" + str(identifier), headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: download_license({env}, {str(identifier)}), {e}")

    if response.status_code == 200:
        form = response.json()
        # remove forbidden keys
        del form["id"]
        del form["organization"]["organization/short-name"]
        del form["organization"]["organization/name"]
        del form["enabled"]
        del form["archived"]
        return form
    else:
        sys.exit(f"ABORT: download_license({env}, {str(identifier)}) responded with {str(response.status_code)}")


def post_license(c, license, env):
    """Post license to environment."""
    license["organization"]["organization/id"] = c[env]["organisation"]
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/licenses/create", headers=headers, json=license)
    except Exception as e:
        sys.exit(f"ERROR: post_license(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_license() responded with {str(response.status_code)}, {response.text}")


def get_licenses(c, env):
    """Get available licenses."""
    print(f"downloading licenses from {env}")
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
        response = requests.get(c[env]["url"].rstrip("/") + "/api/licenses", headers=headers, params=params)
    except Exception as e:
        sys.exit(f"ERROR: get_licenses({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_licenses({env}) responded with {str(response.status_code)}")
