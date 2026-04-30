from django.urls import path
from .views import ProgressSummaryView, DailyProgressListView

urlpatterns = [
    path('summary/', ProgressSummaryView.as_view(), name='progress-summary'),
    path('daily/', DailyProgressListView.as_view(), name='progress-daily'),
]
