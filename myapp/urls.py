
from django.urls import path

from .views import (
    AnalyticsView,
    GetReportMessageAPIView,
    HomePageView,
    LoginView,
    ProfileView,
    ReadMessageAPIView,
    RootView,
    ViewCase,
)

urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('login/', LoginView.as_view(), name='login'),
    path('homepage/', HomePageView.as_view(), name='homepage'),
    path('viewcases/', ViewCase.as_view(), name='viewcases'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('readmessage/', ReadMessageAPIView.as_view(), name='readmessage'),
    path('getReportmsg/', GetReportMessageAPIView.as_view(), name='getReportmsg'),
]
