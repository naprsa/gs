from rest_framework import serializers
from office.models import Feedback


class FeedbackModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["text", "email"]
