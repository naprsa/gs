from rest_framework import generics
from rest_framework.permissions import AllowAny

from office.models import Feedback
from .serializers import FeedbackModelSerializer
from icecream import ic


class CreateFeedbackApiView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackModelSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
