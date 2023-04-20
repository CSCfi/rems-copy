"""Catalogue operations."""
import sys

import requests

from ..forms import get_form, get_forms
from ..workflows import get_workflow, get_workflows
from ..resources import get_resource, get_resources


def copy_catalogue(config, source, destination, check):
    """Copy catalogues from source to destination if name doesn't already exist in destination."""
    source_catalogue_items = get_catalogue_items(config, source)
    destination_catalogue_items = get_catalogue_items(config, destination)
    destination_catalogue_item_names = [dci["localizations"][config["language"]]["title"] for dci in destination_catalogue_items]
    destination_forms = get_forms(config, destination)
    destination_resources = get_resources(config, destination)
    destination_workflows = get_workflows(config, destination)

    skipped = []
    created = []

    for i, sci in enumerate(source_catalogue_items):
        sys.stdout.write(f"\rcopying catalogue items {i+1}/{len(source_catalogue_items)}")
        sys.stdout.flush()
        if sci["localizations"][config["language"]]["title"] not in destination_catalogue_item_names:
            if not check:
                destination_form_id = None
                if sci["formid"] is not None:
                    source_form = get_form(config, source, sci["formid"])
                    for form in destination_forms:
                        if form["form/internal-name"] == source_form["form/internal-name"]:
                            destination_form_id = form["form/id"]
                            break
                if sci["formid"] is not None and destination_form_id is None:
                    print(f"could not find source_form={sci['formid']} from {destination}, skipping this item")
                    break

                destination_resource_id = None
                if sci["resource-id"] is not None:
                    source_resource = get_resource(config, source, sci["resource-id"])
                    for resource in destination_resources:
                        if resource["resid"] == source_resource["resid"]:
                            destination_resource_id = resource["id"]
                            break
                if sci["resource-id"] is not None and destination_resource_id is None:
                    print(f"could not find source_resource={sci['resource-id']} from {destination}, skipping this item")
                    break

                destination_workflow_id = None
                if sci["wfid"] is not None:
                    source_workflow = get_workflow(config, source, sci["wfid"])
                    for workflow in destination_workflows:
                        if workflow["title"] == source_workflow["title"]:
                            destination_workflow_id = workflow["id"]
                            break
                if sci["wfid"] is not None and destination_workflow_id is None:
                    print(f"could not find source_workflow={sci['wfid']} from {destination}, skipping this item")
                    break

                catalogue_data = create_catalogue_item_data(
                    form_id=destination_form_id,
                    resource_id=destination_resource_id,
                    workflow_id=destination_workflow_id,
                    organisation=config[destination]["organisation"],
                    titles=sci["localizations"],
                )
                post_catalogue_item(config, catalogue_data, destination)
            created.append(sci["localizations"][config["language"]]["title"])
        else:
            skipped.append(sci["localizations"][config["language"]]["title"])

    print(f"\nskipped catalogue items that already exist at {destination}: {skipped}")
    print(f"created new catalogue items at {destination}: {created}")


def create_catalogue_item_data(form_id=0, resource_id=0, workflow_id=0, organisation="", titles={}):
    """Create catalogue payload."""
    for _, title in titles.items():
        del title["id"]
        del title["langcode"]

    payload = {
        "form": form_id,
        "resid": resource_id,
        "wfid": workflow_id,
        "organization": {
            "organization/id": organisation,
        },
        "localizations": titles,
        "enabled": True,
        "archived": False,
    }
    return payload


def post_catalogue_item(c, catalogue, env):
    """Post catalogue to environment."""
    catalogue["organization"]["organization/id"] = c[env]["organisation"]
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/catalogue-items/create", headers=headers, json=catalogue)
    except Exception as e:
        sys.exit(f"ERROR: post_catalogue_item(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_catalogue_item() responded with {str(response.status_code)}, {response.text}")


def put_catalogue_item(c, env, catalogue):
    """Put (update) catalogue to environment."""
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.put(c[env]["url"].rstrip("/") + "/api/catalogue-items/edit", headers=headers, json=catalogue)
    except Exception as e:
        sys.exit(f"ERROR: post_catalogue_item(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_catalogue_item() responded with {str(response.status_code)}, {response.text}")


def get_catalogue_items(c, env):
    """Get available catalogue items."""
    print(f"downloading catalogue items from {env}")
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
        response = requests.get(c[env]["url"].rstrip("/") + "/api/catalogue-items", headers=headers, params=params)
    except Exception as e:
        sys.exit(f"ERROR: get_catalogue_items({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_catalogue_items({env}) responded with {str(response.status_code)}")


def get_catalogue_item(c, env, catalogue_id):
    """Get specific catalogue items."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + f"/api/catalogue-items/{catalogue_id}", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_catalogue_item({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_catalogue_item({env}) responded with {str(response.status_code)}")


def create_catalogue_item_id_translator(c, source_catalogue_items, destination_catalogue_items):
    """Create a translation book for converting source catalogue item id to destination catalogue item id."""
    translator = {}

    for sci in source_catalogue_items:
        for dci in destination_catalogue_items:
            if sci["localizations"][c["language"]]["title"] == dci["localizations"][c["language"]]["title"]:
                translator[sci["id"]] = dci["id"]
                break

    return translator
