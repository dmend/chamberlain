#!/usr/bin/env python
#
# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Dynamic Inventory script for ansible.

This script can be used with Ansible to pull node information from the Chef
server.

See: http://www.ansibleworks.com/docs/developing_inventory.html
"""

import argparse
import json

import chef


class ChefInventory:
    def __init__(self):
        self.parser = self._create_parser()
        self.api = chef.autoconfigure()

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description=u'Chef Server Dynamic Inventory for Ansible.'
        )
        parser.add_argument(u'--list', action=u'store_true',
                            help=u'List all nodes.')
        parser.add_argument(u'--host', help=u'Retrieve variable information.')
        return parser

    def _list_all_nodes(self):
        resp = dict()
        with self.api:
            environments = [e[u'name'] for e in chef.Search(u'environment')]
            nodes = chef.Search(u'node')
            for env in environments:
                apis = u'{}_api'.format(env)
                workers = u'{}_worker'.format(env)
                dbs = u'{}_db'.format(env)
                queues = u'{}_queues'.format(env)

                resp[env] = {u'children': [apis, workers, dbs, queues]}
                resp[apis] = [n[u'automatic'][u'ipaddress'] for n in nodes if (
                    n[u'chef_environment'] == env and \
                    u'roles' in n[u'automatic'].keys() and \
                    u'barbican-api' in n[u'automatic'][u'roles']
                )]
                resp[workers] = [n[u'automatic'][u'ipaddress'] for n in nodes \
                    if (
                        n[u'chef_environment'] == env and \
                        u'roles' in n[u'automatic'].keys() and \
                        u'barbican-worker' in n[u'automatic'][u'roles']
                    )
                ]
                resp[dbs] = [n[u'automatic'][u'ipaddress'] for n in nodes if (
                    n[u'chef_environment'] == env and \
                    u'roles' in n[u'automatic'].keys() and \
                    u'barbican-db' in n[u'automatic'][u'roles']
                )]
                resp[queues] = [n[u'automatic'][u'ipaddress'] for n in nodes \
                    if (
                        n[u'chef_environment'] == env and \
                        u'roles' in n[u'automatic'].keys() and \
                        u'barbican-queue' in n[u'automatic'][u'roles']
                    )
                ]
        print(json.dumps(resp))

    def _node_variables(self):
        """Return variables for a specific node.
        
        We're not using this feature, so we return an empty hash instead.
        """
        print(json.dumps(dict()))

    def execute(self):
        args = self.parser.parse_args()
        if args.list:
            self._list_all_nodes()
        else:
            self._node_variables()


def main():
    ci = ChefInventory()
    ci.execute()


if __name__ == '__main__':
    main()

