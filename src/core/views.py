import os

from django.http import HttpResponse
from django.conf import settings


def terms_of_use_view(request):
    pdf = os.path.join(
        settings.BASE_DIR, "core", "settings", "common", "terms-of-use.pdf"
    )
    with open(pdf, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response["Content-Disposition"] = "filename=terms-of-use.pdf"
        return response


def privacy_policy_view(request):
    pdf = os.path.join(
        settings.BASE_DIR, "core", "settings", "common", "privacy-policy.pdf"
    )
    with open(pdf, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response["Content-Disposition"] = "filename=privacy-policy.pdf"
        return response
