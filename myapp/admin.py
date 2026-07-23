from django.contrib import admin

from .models import Case, ReportMessage

# Register your models here.
admin.site.register(Case)
admin.site.register(ReportMessage)