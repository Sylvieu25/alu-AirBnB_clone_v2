#!/usr/bin/python3
"""Fabric script that distributes an archive to the web servers."""
import os
from fabric.api import env, put, run, settings

env.hosts = ['54.91.248.231', '100.27.23.115']
env.skip_bad_hosts = True
env.timeout = 10


def do_deploy(archive_path):
    """Deploy the archive at archive_path to the web servers.

    Returns False if the archive does not exist or any step fails,
    otherwise returns True.
    """
    if not os.path.isfile(archive_path):
        return False
    name = os.path.basename(archive_path)
    base = name.split('.')[0]
    release = "/data/web_static/releases/{}".format(base)
    tmp = "/tmp/{}".format(name)
    with settings(warn_only=True):
        if put(archive_path, tmp).failed:
            return False
        commands = [
            "mkdir -p {}/".format(release),
            "tar -xzf {} -C {}/".format(tmp, release),
            "rm {}".format(tmp),
            "mv {0}/web_static/* {0}/".format(release),
            "rm -rf {}/web_static".format(release),
            "rm -rf /data/web_static/current",
            "ln -s {}/ /data/web_static/current".format(release),
        ]
        for command in commands:
            if run(command).failed:
                return False
    print("New version deployed!")
    return True
