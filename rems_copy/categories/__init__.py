"""Category operations."""
import sys

import requests

from ..catalogue import get_catalogue_items, get_catalogue_item, create_catalogue_item_id_translator, put_catalogue_item


def copy_categories(config, source, destination):
    """Copy categories from source to destination if name doesn't already exist in destination and update categories to catalogue items."""
    source_categories = get_categories(config, source)
    destination_categories = get_categories(config, destination)
    destination_category_names = [dc["category/title"][config["language"]] for dc in destination_categories]

    # First run: create categories
    print("categories stage 1/3: create categories")
    skipped = []
    created = []

    for i, sc in enumerate(source_categories):
        sys.stdout.write(f"\rcopying categories {i+1}/{len(source_categories)}")
        sys.stdout.flush()
        if sc["category/title"][config["language"]] not in destination_category_names:
            post_category(config, destination, sc)
            created.append(sc["category/title"][config["language"]])
        else:
            skipped.append(sc["category/title"][config["language"]])

    print(f"\nskipped categories that already exist at {destination}: {skipped}")
    print(f"created new categories at {destination}: {created}")

    # Second run: update category children
    print("categories stage 2/3: update category children")
    skipped = []
    updated = []

    destination_categories = get_categories(config, destination)
    category_id_translator = create_category_id_translator(config, source_categories, destination_categories)

    for i, sc in enumerate(source_categories):
        sys.stdout.write(f"\rupdating category children {i+1}/{len(source_categories)}")
        sys.stdout.flush()
        if len(sc.get("category/children", [])):
            # Get children from source and translate to destination format
            destination_children = sc["category/children"]
            for dc in destination_children:
                dc["category/id"] = category_id_translator[dc["category/id"]]
            # Get destination parent and send changes
            for dc in destination_categories:
                if category_id_translator[sc["category/id"]] == dc["category/id"]:
                    dc["category/children"] = destination_children
                    update_category_children(config, destination, dc)
                    break
            updated.append(sc["category/title"][config["language"]])
        else:
            skipped.append(sc["category/title"][config["language"]])

    print(f"\nskipped categories that don't have children at {source}: {skipped}")
    print(f"updated categories with children at {destination}: {updated}")

    # Third run: update categories to catalogue items
    print("categories stage 3/3: update catalogue items")
    skipped = []
    updated = []

    source_catalogue_items = get_catalogue_items(config, source)
    destination_catalogue_items = get_catalogue_items(config, destination)
    catalogue_item_id_translator = create_catalogue_item_id_translator(config, source_catalogue_items, destination_catalogue_items)

    for i, sci in enumerate(source_catalogue_items):
        sys.stdout.write(f"\rupdating catalogue items {i+1}/{len(source_catalogue_items)}")
        sys.stdout.flush()
        source_catalogue_item = get_catalogue_item(config, source, sci["id"])
        if len(source_catalogue_item["categories"]):
            destination_catalogue_item = get_catalogue_item(config, destination, catalogue_item_id_translator[sci["id"]])
            # Parse categories
            categories = [{"category/id": category_id_translator[scic["category/id"]]} for scic in source_catalogue_item["categories"]]
            # Get mandatory titles and remove disallowed keys
            localizations = destination_catalogue_item["localizations"]
            for _, localization in localizations.items():
                del localization["id"]
                del localization["langcode"]
            new_catalogue_item = {
                "id": destination_catalogue_item["id"],
                "localizations": localizations,
                "categories": categories
            }
            put_catalogue_item(config, destination, new_catalogue_item)
            updated.append(sci["localizations"][config["language"]]["title"])
        else:
            skipped.append(sci["localizations"][config["language"]]["title"])

    print(f"\nskipped catalogue items that don't have categories at {source}: {skipped}")
    print(f"updated catalogue items with categories at {destination}: {updated}")



def get_categories(c, env):
    """Get available categories."""
    print(f"downloading categories from {env}")

    headers = {
        "accept": "application/json",
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.get(c[env]["url"].rstrip("/") + "/api/categories", headers=headers)
    except Exception as e:
        sys.exit(f"ERROR: get_categories({env}), {e}")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit(f"ABORT: get_categories({env}) responded with {str(response.status_code)}")


def create_category_id_translator(c, source_categories, destination_categories):
    """Create a translation book for converting source category id to destination category id."""

    translator = {}

    for sc in source_categories:
        for dc in destination_categories:
            if sc["category/title"][c["language"]] == dc["category/title"][c["language"]]:
                translator[sc["category/id"]] = dc["category/id"]
                break

    return translator


def post_category(c, env, category):
    """Post category to environment."""

    # Make children empty, update them later
    category["category/children"] = []
    # Remove disallowed key
    del category["category/id"]

    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.post(c[env]["url"].rstrip("/") + "/api/categories", headers=headers, json=category)
    except Exception as e:
        sys.exit(f"ERROR: post_category(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: post_category() responded with {str(response.status_code)}, {response.text}")


def update_category_children(c, env, category):
    """Update category children."""

    headers = {
        "x-rems-api-key": c[env]["key"],
        "x-rems-user-id": c[env]["username"],
    }
    try:
        response = requests.put(c[env]["url"].rstrip("/") + "/api/categories", headers=headers, json=category)
    except Exception as e:
        sys.exit(f"ERROR: update_category_children(), {e}")

    if response.status_code == 200:
        pass
    else:
        sys.exit(f"ABORT: update_category_children() responded with {str(response.status_code)}, {response.text}")
