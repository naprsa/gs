import os
from decouple import config
from icecream import ic
from .base import BASE_DIR


def get_auth_key(file):
    with open(file, "r") as f:
        auth_key = f.read()
    return auth_key


AUTH_KEY = os.path.join(BASE_DIR, "core", "settings", "common", "AuthKey_F3WX8L6R6C.p8")
APPLE_APP_STORE_URL = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_APP_STORE_SANDBOX_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
APPLE_ID_CLIENT = config("APPLE_ID_CLIENT")  # Service ID
APPLE_ID_TEAM = config("APPLE_ID_TEAM")
APPLE_ID_KEY = config("APPLE_ID_KEY")
APPLE_ID_SECRET = get_auth_key(AUTH_KEY)
APPLE_IN_APP_PURCHASES_KEY = config("APPLE_IN_APP_PURCHASES_KEY")
APPLE_IN_APP_PURCHASES_ID = config("APPLE_IN_APP_PURCHASES_ID")
