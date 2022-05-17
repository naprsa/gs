from django.http import HttpResponse, Http404
from django.shortcuts import render
from .models import PrintLayout

# Create your views here.


def get_pdf(request, deck_uid):
    try:
        layout = PrintLayout.objects.get(deck__uid=deck_uid)
    except PrintLayout.DoesNotExist:
        return Http404()
    with open(layout.file.path, "rb") as pdf:

        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=print_layout.pdf"
        return response
