"""Resource operations."""
import sys

import requests

from ..licenses import get_licenses


def copy_resources(config, source, destination):
    """Copy resources from source to destination if name doesn't already exist in destination."""
    source_resources = get_resources(config, source)
    destination_resources = get_resources(config, destination)
    destination_resource_names = [dr["resid"] for dr in destination_resources]
    destination_licenses = get_licenses(config, destination)
    destination_licenses_dict = {}
    for dl in destination_licenses:
        destination_licenses_dict[dl["localizations"][config["language"]]["title"]] = dl["id"]

    skipped = []
    created = []

    for i, sr in enumerate(source_resources):
        sys.stdout.write(f"\rcopying resources {i+1}/{len(source_resources)}")
        sys.stdout.flush()
        if sr["resid"] not in destination_resource_names:
            resource_data = create_resource_data(
                config=config,
                resource=sr["resid"],
                organisation=config[source]["organisation"],
                resource_licenses=sr["licenses"],
                destination_licenses=destination_licenses_dict,
            )
            post_resource(config, resource_data, destination)
            created.append(sr["resid"])
        else:
            skipped.append(sr["resid"])

    print(f"\nskipped resources that already exist at {destination}: {skipped}")
    print(f"\ncreated new resources at {destination}: {created}")


def create_resource_data(config={}, resource="", organisation="", resource_licenses=[], destination_licenses={}):
    """Create resource payload."""
    payload = {
        "resid": resource,
        "organization": {"organization/id": organisation},
        "licenses": [destination_licenses[rl["localizations"][config["language"]]["title"]] for rl in resource_licenses],
    }
    return payload


def post_resource(c, resource, env):
    """Post resource to environment."""
    resource["organization"]["organization/id"] = c[env]["organisation"]
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/resources/create", headers=headers, json=resource)
    except Exception as e:
        sys.exit(f"ERROR: post_resource(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_resource() responded with {str(response.status_code)}, {response.text}")


def get_resources(c, env):
    """Get available resources."""
    print(f"downloading resources from {env}")
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
        response = requests.get(c[env]["url"].rstrip("/") + "/api/resources", headers=headers, params=params)
    except Exception as e:
        sys.exit(f"ERROR: get_resources({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_resources({env}) responded with {str(response.status_code)}")


def get_resource(c, env, resource_id):
    """Get specific resources."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + f"/api/resources/{resource_id}", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_resource({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_resource({env}) responded with {str(response.status_code)}")
