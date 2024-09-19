# from django.urls import path
# from devices.views import EventCreateView, EventListView, EventSummaryView

# urlpatterns = [
#     path('events/', EventCreateView.as_view(), name='create_event'),
#     path('events/query/', EventListView.as_view(), name='query_events'),
#     path('events/summary/', EventSummaryView.as_view(), name='event_summary'),
# ]
from django.urls import path
from .views import DeviceAPIView, EventCreateAPIView, EventListAPIView, EventSummaryAPIView

urlpatterns = [
    path('devices/', DeviceAPIView.as_view()),  # For listing and creating devices
    path('devices/<int:pk>/', DeviceAPIView.as_view()),  # For retrieve, update, delete
    path('devices/<int:pk>/activate/', DeviceAPIView.as_view(), {'action': 'activate'}),  # Activate a device
    path('devices/<int:pk>/deactivate/', DeviceAPIView.as_view(), {'action': 'deactivate'}),  # Deactivate a device
    path('events/', EventCreateAPIView.as_view()),  # To create a new event
    path('events/list/', EventListAPIView.as_view()),  # Query events by device and date range
    path('events/summary/', EventSummaryAPIView.as_view()),  # Get summary report for events
]
