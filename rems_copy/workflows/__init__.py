"""workflow operations."""
import sys

import requests

from ..forms import get_forms


def copy_workflows(config, source, destination, check):
    """Copy workflows from source to destination if name doesn't already exist in destination."""
    source_workflows = get_workflows(config, source)
    destination_workflows = get_workflows(config, destination)
    destination_workflow_names = [dw["title"] for dw in destination_workflows]
    destination_forms = get_forms(config, destination)
    destination_forms_dict = {}
    for df in destination_forms:
        destination_forms_dict[df["form/title"]] = df["form/id"]

    skipped = []
    created = []

    for i, sw in enumerate(source_workflows):
        sys.stdout.write(f"\rcopying workflows {i+1}/{len(source_workflows)}")
        sys.stdout.flush()
        if sw["title"] not in destination_workflow_names:
            if not check:
                workflow_data = create_workflow_data(
                    title=sw["title"],
                    organisation=config[source]["organisation"],
                    workflow_type=sw["workflow"]["type"],
                    workflow_forms=sw["workflow"]["forms"],
                    destination_forms=destination_forms_dict,
                )
                post_workflow(config, workflow_data, destination)
            created.append(sw["title"])
        else:
            skipped.append(sw["title"])

    print(f"\nskipped workflows that already exist at {destination}: {skipped}")
    print(f"created new workflows at {destination}: {created}")


def create_workflow_data(title="", organisation="", workflow_type="", workflow_forms=[], destination_forms={}):
    """Create workflow payload."""
    payload = {
        "organization": {
            "organization/id": organisation,
        },
        "title": title,
        "forms": [{"form/id": destination_forms[wf["form/internal-name"]]} for wf in workflow_forms],
        "type": workflow_type,
        "handlers": [],
    }
    return payload


def post_workflow(c, workflow, env):
    """Post workflow to environment."""
    workflow["organization"]["organization/id"] = c[env]["organisation"]
    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/workflows/create", headers=headers, json=workflow)
    except Exception as e:
        sys.exit(f"ERROR: post_workflow(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_workflow() responded with {str(response.status_code)}, {response.text}")


def get_workflows(c, env):
    """Get available workflows."""
    print(f"downloading workflows from {env}")
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
        response = requests.get(c[env]["url"].rstrip("/") + "/api/workflows", headers=headers, params=params)
    except Exception as e:
        sys.exit(f"ERROR: get_workflows({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_workflows({env}) responded with {str(response.status_code)}")


def get_workflow(c, env, workflow_id):
    """Get specific workflow."""
    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + f"/api/workflows/{workflow_id}", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_workflow({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_workflow({env}) responded with {str(response.status_code)}")
