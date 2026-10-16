#!/usr/bin/python3
"""Fabric script that generates a .tgz archive from web_static."""
import os
from datetime import datetime
from fabric.api import local, settings


def do_pack():
    """Pack the web_static folder into a timestamped .tgz in versions.

    Returns the archive path if it was generated correctly,
    otherwise returns None.
    """
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    path = "versions/web_static_{}.tgz".format(stamp)
    print("Packing web_static to {}".format(path))
    with settings(warn_only=True):
        if local("mkdir -p versions").failed:
            return None
        if local("tar -cvzf {} web_static".format(path)).failed:
            return None
    print("web_static packed: {} -> {}Bytes".format(
        path, os.path.getsize(path)))
    return path
