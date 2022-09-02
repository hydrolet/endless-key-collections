#!/usr/bin/env python3

import argparse
import configparser
import json
import os


def parse_channel_from_config(config, id):
    channel = {
        'id': id,
        'include_node_ids': [],
        'exclude_node_ids': [],
    }

    section = f'kolibri-{id}'
    if section not in config.sections():
        return channel

    channel_section = config[section]
    include_node_ids = channel_section.get('include_node_ids', '').split()
    exclude_node_ids = channel_section.get('exclude_node_ids', '').split()

    channel['include_node_ids'] = include_node_ids
    channel['exclude_node_ids'] = exclude_node_ids

    return channel


def ini2json(f, output='collections', metadata='metadata'):
    filename, _ext = os.path.splitext(os.path.basename(f))
    metadata_file = os.path.join(metadata, f'{filename}.json')
    output_path = os.path.join(output, f'{filename}.json')

    config = configparser.ConfigParser()
    config.read(f)

    out = {'channels': [], 'metadata': {}}

    channel_ids = config['kolibri']['install_channels']
    channels = channel_ids.split()
    for id in channels:
        channel = parse_channel_from_config(config, id)
        out['channels'].append(channel)

    with open(metadata_file) as f:
        out['metadata'] = json.load(f)
        out['metadata']['channels'] = len(channels)

    with open(output_path, 'w') as output_file:
        json.dump(out, output_file, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert collection .ini files to manifest.json')
    parser.add_argument('files', metavar='INI_FILE', type=str, nargs='+',
                        help='A .ini file to convert to manifest.json')
    parser.add_argument('-o', '--output', type=str, default='collections',
                        help='The output directory, collections by default')
    parser.add_argument('-m', '--metadata', type=str, default='metadata',
                        help='The metadata directory, metadata by default')

    args = parser.parse_args()
    for f in args.files:
        ini2json(f, args.output, args.metadata)
