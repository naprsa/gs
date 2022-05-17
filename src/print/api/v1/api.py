from celery.result import AsyncResult
from django.urls import reverse
from icecream import ic
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.celery import app
from game.models import Deck
from print.models import PrintLayout
from print.tasks import generate_layout


class GetPrintLayout(APIView):
    def get(self, request, deck_uid, **kwargs):
        pin = request.GET.get("pin")
        deck = get_object_or_404(Deck.objects.filter(), uid=deck_uid)

        if not deck.check_pin(pin):
            data = {"pin": "Invalid pin"}
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        print_layout, created = PrintLayout.objects.get_or_create(deck=deck)
        if created or (not created and deck.updated > print_layout.updated):
            job = generate_layout.apply_async((deck_uid,), ignore_result=False)
            print_layout.task = job.id
            print_layout.save(update_fields=["task"])
            response = Response({"code": job.state})
            return response
        else:
            job = AsyncResult(print_layout.task, app=app)
            data = job.result or job.state
            data = {"code": job.state}
            if job.state == "SUCCESS":
                url = request.build_absolute_uri(
                    reverse("print:get_pdf", kwargs={"deck_uid": deck_uid})
                )
                data["url"] = url.replace("http", "https")
                print_layout.counter += 1
                print_layout.save(update_fields=["counter"])
            elif job.state == "FAILURE":
                job = generate_layout.apply_async((deck_uid,), ignore_result=False)
                print_layout.task = job.id
                print_layout.save(update_fields=["task"])
                data = {"code": "failure", "status": "generator restarted"}
            return Response(data)
