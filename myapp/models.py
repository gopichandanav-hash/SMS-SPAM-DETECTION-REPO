from django.db import models

# Create your models here.

class Case(models.Model):
    case_number = models.CharField(max_length=100)
    case_sender = models.CharField(max_length=100)
    case_title = models.CharField(max_length=200)
    case_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_title


class ReportMessage(models.Model):
    sender = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender or 'Unknown'} - {self.message[:50]}"
    