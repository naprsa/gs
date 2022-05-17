import os
from decouple import config
from .base import BASE_DIR

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_BILLING_FILE = config("GOOGLE_BILLING_FILE")

GOOGLE_CREDENTIALS_FILE_PATH = os.path.join(
    BASE_DIR,
    "core",
    "settings",
    "common",
    GOOGLE_BILLING_FILE,
)
GOOGLE_ANDROID_PUBLISHER_APP = config("GOOGLE_ANDROID_PUBLISHER_APP")
