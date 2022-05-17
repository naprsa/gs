import json
import os
from django.http import JsonResponse
from core import settings


def apple_verification(request):
    path = os.path.join(settings.BASE_DIR, "core", "settings", "common")
    with open(os.path.join(path, "apple-app-site-association.json")) as file:
        file_json = json.load(file)
        response = JsonResponse(file_json, content_type="application/json")
        return response
