from rest_framework.serializers import ModelSerializer
from .models import Case

class CaseSerializer(ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

from rest_framework import serializers

class SmsSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    body = serializers.CharField()


class SmsRequestSerializer(serializers.Serializer):
    messages = SmsSerializer(many=True)