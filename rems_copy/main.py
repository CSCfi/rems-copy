"""REMS Copy."""
import os
import sys
import json
import argparse

from .licenses import copy_licenses
from .forms import copy_forms
from .resources import copy_resources
from .workflows import copy_workflows
from .catalogue import copy_catalogue


def load_config(path):
    """Load configuration file."""
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.loads(f.read())
            return data
    else:
        sys.exit(f"ERROR: load_config({path}), file not found")


def parse_arguments(arguments):
    """Parse command line arguments and options."""
    parser = argparse.ArgumentParser(description="This tool copies REMS items from one instance to another")
    parser.add_argument("items", choices=["licenses", "forms", "resources", "workflows", "catalogue", "all"], help="items to move")
    parser.add_argument("source", help="source environment where items are downloaded from")
    parser.add_argument("destination", help="destination environment where items are uploaded to")
    parser.add_argument("-c", "--config", default="config.json", help="path to JSON configuration file, default='./config.json'")
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    return parser.parse_args(arguments)


def main(arguments=None):
    """Run script."""
    a = parse_arguments(arguments)
    config = load_config(a.config)

    if a.items == "licenses":
        copy_licenses(config, a.source, a.destination)
    if a.items == "forms":
        copy_forms(config, a.source, a.destination)
    if a.items == "resources":
        copy_resources(config, a.source, a.destination)
    if a.items == "workflows":
        copy_workflows(config, a.source, a.destination)
    if a.items == "catalogue":
        copy_catalogue(config, a.source, a.destination)
    if a.items == "all":
        copy_licenses(config, a.source, a.destination)
        copy_forms(config, a.source, a.destination)
        copy_resources(config, a.source, a.destination)
        copy_workflows(config, a.source, a.destination)
        copy_catalogue(config, a.source, a.destination)


if __name__ == "__main__":
    main()
