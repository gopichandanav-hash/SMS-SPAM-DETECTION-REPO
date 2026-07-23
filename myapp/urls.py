
from django.urls import path

from .views import LoginView, HomePageView, ReadMessageAPIView, GetReportMessageAPIView, ViewCase, ProfileView, AnalyticsView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('homepage/', HomePageView.as_view(), name='homepage'),
    path('viewcases/', ViewCase.as_view(), name='viewcases'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('readmessage/', ReadMessageAPIView.as_view(), name='readmessage'),
    path('getReportmsg/', GetReportMessageAPIView.as_view(), name='getReportmsg'),
]
