from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


class RootView(View):
    def get(self, request):
        return HttpResponse("SMS Spam Detection API is running", content_type="text/plain")

    def head(self, request):
        return HttpResponse(status=200)
# Create your views here.

from .models import ReportMessage
from .serializers import SmsRequestSerializer
from .ml_model import predict_sms


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "admin" and password == "admin123":
            request.session["fixed_login_authenticated"] = True
            return redirect("homepage")

        messages.error(request, "Invalid username or password.")
        return render(request, "login.html")
class HomePageView(View):
    def get(self, request):
        if not request.session.get("fixed_login_authenticated"):
            return redirect("login")

        return render(request, "homepage.html")
class ViewCase(View):
    def get(self, request):
        if not request.session.get('fixed_login_authenticated'):
            return redirect('login')

        reports = ReportMessage.objects.order_by('-created_at')
        return render(request, 'viewcases.html', {'reports': reports})


class ProfileView(View):
    def get(self, request):
        if not request.session.get('fixed_login_authenticated'):
            return redirect('login')
        return render(request, 'profile.html')


class AnalyticsView(View):
    def get(self, request):
        if not request.session.get('fixed_login_authenticated'):
            return redirect('login')

        reports = ReportMessage.objects.order_by('-created_at')
        report_count = reports.count()

        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_counts = [0, 0, 0, 0, 0, 0, 0]

        for report in reports:
            weekday = report.created_at.weekday()
            day_counts[weekday] += 1

        chart_data = list(zip(day_labels, day_counts))

        return render(request, 'analytics.html', {
            'reports': reports,
            'report_count': report_count,
            'chart_data': chart_data,
        })
    
# class ReadMessageAPI(APIView):
#     def post(self, request):
#         print(request.data)
        
#         return Response(status=HTTP_200_OK)

class ReadMessageAPIView(APIView):

    def post(self, request):
        print("data recieved")
        serializer = SmsRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST
            )

        messages = serializer.validated_data["messages"]

        results = []

        # for sms in messages:
        #     print("Processing SMS")

        #     prediction = predict_sms(sms["body"])

        #     results.append({
        #         "index": sms["index"],
        #         "prediction": prediction
        #     })
        import traceback

        for sms in messages:
            try:
                print("Processing SMS")

                prediction = predict_sms(sms["body"])

                print("Prediction:", prediction)

                results.append({
                    "index": sms["index"],
                    "prediction": prediction
                })

            except Exception as e:
                traceback.print_exc()
                return Response(
                    {"error": str(e)},
                    status=500
                )

        return Response({
            "count": len(results),
            "results": results
        })


class GetReportMessageAPIView(APIView):
    def post(self, request):
        print(" data:", request.data)

        payload = request.data
        if isinstance(payload, (list, tuple)):
            items_to_save = payload
        else:
            if hasattr(payload, "items"):
                payload = dict(payload)
            else:
                payload = {"raw": payload}

            if isinstance(payload.get("messages"), list):
                items_to_save = payload["messages"]
            elif isinstance(payload.get("message"), list):
                items_to_save = payload["message"]
            else:
                items_to_save = [payload]

        created_reports = []

        for item in items_to_save:
            if isinstance(item, dict):
                nested_message = item.get("message", item)
                if isinstance(nested_message, dict):
                    sender = item.get("sender") or nested_message.get("address") or item.get("address") or ""
                    message_text = nested_message.get("body") or nested_message.get("message") or ""
                    category = item.get("category") or "spam"
                    report_payload = item
                else:
                    sender = item.get("sender", "")
                    message_text = str(nested_message)
                    category = item.get("category", "spam")
                    report_payload = item
            else:
                sender = ""
                message_text = str(item)
                category = "spam"
                report_payload = {"value": item}

            report_message = ReportMessage.objects.create(
                sender=str(sender),
                message=str(message_text),
                category=str(category),
                payload=report_payload,
            )
            created_reports.append({
                "id": report_message.id,
                "sender": report_message.sender,
                "message": report_message.message,
                "category": report_message.category,
            })

        return Response({
            "message": "Data received",
            "saved_count": len(created_reports),
            "data": created_reports,
        }, status=HTTP_200_OK)
    
