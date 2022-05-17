from rest_framework import serializers


class FilterDeckSerialiser(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter()
        return super().to_representation(data)
