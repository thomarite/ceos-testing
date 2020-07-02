#!/usr/bin/env python

import os
import argparse
from nornir import InitNornir
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.text import template_file
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_config
from nornir.plugins.tasks import networking
from nornir.plugins.tasks import files

__author__ = "Tomas Morales"
__version__ = "0.0.1"

def parse_args():
    parser = argparse.ArgumentParser(description="Building Config")
    parser.add_argument("-c", "--commit", action='store_true', help="Commit Config")
    parser.add_argument("-b", "--build",  action='store', choices=['bgp', 'isis'], help="Config to be built")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s (version {})".format(__version__),
    )

    # if len(sys.argv) <= 1:
    #    sys.argv.append('--help')

    args = parser.parse_args()
    return args


def get_hostname(task):
    return task.run(task=networking.netmiko_send_command, command_string="show run | grep -i hostname")

def render_config(task, section):
    data = task.run(task=load_yaml,file=f'./inventory/host_vars/{task.host}.yaml')
    task.host[section] = data.result[section]
    r = task.run(task=template_file, template=f"{task.host.platform}-{section}.j2", path="./templates", **task.host)
    task.host[section] = r[0].result

def write_config(task, section):
    cfg_path = f"render/{task.host}/"
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)
    filename = f"{cfg_path}{section}.txt"
    content = task.host[section]
    result = task.run(task=files.write_file, filename=filename, content=content)

def deploy_config(task, section, dry_run=True):
    cfg_path = f"render/{task.host}/"
    filename = f"{cfg_path}{section}.txt"
    with open(filename, "r") as f:
      cfg = f.read()
    result = task.run(task=networking.napalm_configure, configuration=cfg, dry_run=dry_run)

def main():
    args = parse_args()
    nr = InitNornir(config_file="./config.yaml")
    dry_run = True
    if args.commit:
        dry_run = False
    build = 'bgp'
    if args.build:
        build = args.build
    """
    results = nr.run(task=get_hostname)
    #import ipdb; ipdb.set_trace()
    for host in results:
        print("-" * 12)
        print(f"hostname: %s" % host)
        print(f"task: %s" % results[host][1].name)
        print(f"task result: %s" % results[host][1].result)
        print()
    """
    #nr = nr.filter(name="r1")
    nr.run(task=render_config, section=build)
    nr.run(task=write_config, section=build)
    results = nr.run(task=deploy_config, section=build, dry_run=dry_run)
    #import ipdb; ipdb.set_trace()
    for host in results:
        print("-" * 12)
        print(f"hostname: %s" % host)
        print(f"task: %s for %s" % (results[host][0].name, build))
        print(f"failed: %s" % results[host][1].failed)
        print(f"logs: %s" % results[host][1].result)
        print(f"changed: %s" % results[host][0].changed)
        print("diff:")
        print(results[host][1].diff)
        print()

if __name__ == "__main__":
    main()
