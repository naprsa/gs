import re
from celery.app import shared_task
from stats.models import DiskSpaceInfo
from core.services import send_message
from .utils import get_disk_space
from icecream import ic


@shared_task
def collect_disk_info_task():
    info = get_disk_space()
    DiskSpaceInfo.objects.create(
        free=info.get("free", 0),
        used=info.get("used", 0),
        total=info.get("total", 0),
    )
    if info.get("free", None):
        sp = re.search(r"\d+", info["free"])
        if int(sp.group(0)) <= 10:
            subj = "Disk info alert"
            message = (
                f"Free disk space below the acceptable threshold({info.get('free')})!"
                f"\nPlease increase your disk space!"
            )
            send_message(subj, message, alert=True)
    return "Ok"
