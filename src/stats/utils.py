import shutil

from hurry.filesize import size, alternative


def get_disk_space():
    space = dict()
    total, used, free = shutil.disk_usage("/")
    space["total"] = size(total, system=alternative)
    space["used"] = size(used, system=alternative)
    space["free"] = size(free, system=alternative)

    return space
