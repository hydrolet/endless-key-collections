#!/usr/bin/env python3

import hashlib
import argparse
import configparser
import json
import os
from collections import OrderedDict


ALLOWED_TAGS = ["highlight", "skill", "career", "curious"]


def parse_channel_from_config(config, id):
    channel = {
        "id": id,
        "include_node_ids": [],
        "exclude_node_ids": [],
    }

    section = f"kolibri-{id}"
    if section not in config.sections():
        return channel

    channel_section = config[section]
    include_node_ids = channel_section.get("include_node_ids", "").split()
    exclude_node_ids = channel_section.get("exclude_node_ids", "").split()

    channel["include_node_ids"] = include_node_ids
    channel["exclude_node_ids"] = exclude_node_ids

    # FIXME setting channel version to 0 for now, so Kolibri ContentManifest validates
    channel["version"] = 0

    return channel


def parse_metadata_from_section(metadata_section):
    return OrderedDict(
        title=metadata_section.get("title"),
        subtitle=metadata_section.get("subtitle"),
        description=metadata_section.get("description"),
        required_gigabytes=int(metadata_section.get("required_gigabytes")),
    )


def parse_contentnode_extras(config):
    def is_tag_valid(tag):
        return tag in ALLOWED_TAGS

    section_names = []
    for section in config.sections():
        if section.startswith("contentnodeextras-"):
            section_names.append(section)

    tagged_node_ids = []
    for name in section_names:
        section = config[name]
        # FIXME validate that the node_id is included
        node_id = name.split("-")[1]
        tags = section.get("tags", "").split()
        tagged_node_ids.append(
            OrderedDict(
                node_id=node_id,
                tags=list(filter(is_tag_valid, tags)),
            )
        )

    return tagged_node_ids


# Copied from kolibri/core/content/utils/content_manifest.py
def _get_channels_list_hash(channels_list):
    return hashlib.md5(json.dumps(channels_list, sort_keys=True).encode()).hexdigest()


def ini2json(f, output="collections"):
    config = configparser.ConfigParser()
    config.read(f)

    out = {"channels": []}

    channel_ids = config["kolibri"]["install_channels"]
    for id in channel_ids.split():
        channel = parse_channel_from_config(config, id)
        out["channels"].append(channel)

    out["channel_list_hash"] = _get_channels_list_hash(out["channels"])

    if "metadata" in config:
        out["metadata"] = parse_metadata_from_section(config["metadata"])
        tagged_node_ids = parse_contentnode_extras(config)
        if tagged_node_ids:
            out["metadata"]["tagged_node_ids"] = tagged_node_ids

    filename, _ext = os.path.splitext(os.path.basename(f))
    output_path = os.path.join(output, f"{filename}.json")
    with open(output_path, "w") as output_file:
        json.dump(out, output_file, indent=2)
        output_file.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert collection .ini files to manifest.json"
    )
    parser.add_argument(
        "files",
        metavar="INI_FILE",
        type=str,
        nargs="+",
        help="A .ini file to convert to manifest.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="collections",
        help="The output directory, collections by default",
    )

    args = parser.parse_args()
    for f in args.files:
        ini2json(f, args.output)
