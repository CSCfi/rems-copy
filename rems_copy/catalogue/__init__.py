"""Catalogue operations."""
import sys

import requests

from ..forms import get_form, get_forms
from ..workflows import get_workflow, get_workflows


def copy_catalogue(config, source, destination):
    """Copy catalogues from source to destination if name doesn't already exist in destination."""
    source_catalogue_items = get_catalogue_items(config, source)
    destination_catalogue_items = get_catalogue_items(config, destination)
    destination_catalogue_item_names = [dci["localizations"]["en"]["title"] for dci in destination_catalogue_items]
    destination_forms = get_forms(config, destination)
    destination_workflows = get_workflows(config, destination)

    skipped = []
    created = []

    for i, sci in enumerate(source_catalogue_items):
        sys.stdout.write(f"\rcopying catalogue items {i+1}/{len(source_catalogue_items)}")
        sys.stdout.flush()
        if sci["localizations"]["en"]["title"] not in destination_catalogue_item_names:

            source_form = get_form(config, source, sci["formid"])
            destination_form_id = 0
            for form in destination_forms:
                if form["form/internal-name"] == source_form["form/internal-name"]:
                    destination_form_id = form["form/id"]
                    break
            if destination_form_id == 0:
                print(f"could not find form={source_form['form/internal-name']} from {destination}, skipping this item")
                break

            source_workflow = get_workflow(config, source, sci["wfid"])
            destination_workflow_id = 0
            for workflow in destination_workflows:
                if workflow["title"] == source_workflow["title"]:
                    destination_workflow_id = workflow["id"]
            if destination_workflow_id == 0:
                print(f"could not find workflow={source_workflow['title']} from {destination}, skipping this item")
                break

            catalogue_data = create_catalogue_item_data(
                form_id=destination_form_id,
                resource_id=sci["resource-id"],
                workflow_id=destination_workflow_id,
                organisation=config[destination]["organisation"],
                titles=sci["localizations"],
            )
            post_catalogue_item(config, catalogue_data, destination)
            created.append(sci["localizations"]["en"]["title"])
        else:
            skipped.append(sci["localizations"]["en"]["title"])

    print(f"\nskipped catalogue items that already exist at {destination}: {skipped}")
    print(f"\ncreated new catalogue items at {destination}: {created}")


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
