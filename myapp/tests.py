from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import ReportMessage
from . import ml_model


class ReportMessageAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_report_message(self):
        payload = {
            "sender": "admin",
            "message": "Suspicious SMS detected",
            "category": "spam"
        }

        response = self.client.post(reverse("getReportmsg"), payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReportMessage.objects.count(), 1)
        report = ReportMessage.objects.get()
        self.assertEqual(report.payload["message"], "Suspicious SMS detected")

    def test_create_report_message_from_nested_payload(self):
        payload = {
            "message": {
                "index": 1,
                "address": "JD-620014-P",
                "body": "Suspicious SMS detected",
                "date": 1784696493959,
            }
        }

        response = self.client.post(reverse("getReportmsg"), payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReportMessage.objects.count(), 1)
        report = ReportMessage.objects.get()
        self.assertEqual(report.sender, "JD-620014-P")
        self.assertEqual(report.message, "Suspicious SMS detected")

    def test_predict_sms_returns_fallback_when_model_load_fails(self):
        with patch.object(ml_model, "load_model", side_effect=ValueError("boom")):
            ml_model.MODEL = None
            ml_model.TOKENIZER = None
            result = ml_model.predict_sms("Win a free prize now")

        self.assertEqual(result, "ham")
