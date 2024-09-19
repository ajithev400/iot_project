
from .models import Event, Device
from django.db import transaction
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class EventService:
    @staticmethod
    @transaction.atomic
    def store_event(device_id, temperature, event_time):
        try:
            device = Device.objects.get(id=device_id)
            event = Event.objects.create(device=device, temperature=temperature, event_time=event_time)
            return event
        except Device.DoesNotExist:
            raise ObjectDoesNotExist(f"Device with ID {device_id} not found")

    @staticmethod
    def get_events_by_device_and_date_range(device_id, start_date, end_date):
        return Event.objects.filter(device_id=device_id, event_time__range=[start_date, end_date])

    @staticmethod
    def get_event_summary(device_id, start_date, end_date):
        events = Event.objects.filter(device_id=device_id, event_time__range=[start_date, end_date])
        return events.aggregate(
            max_temp=models.Max('temperature'),
            min_temp=models.Min('temperature'),
            avg_temp=models.Avg('temperature')
        )

    @staticmethod
    @transaction.atomic
    def activate_device(device_id):
        try:
            device = Device.objects.get(id=device_id)
            device.status = 'online'
            device.save()
            return device
        except Device.DoesNotExist:
            raise ObjectDoesNotExist(f"Device with ID {device_id} not found")

    @staticmethod
    @transaction.atomic
    def deactivate_device(device_id):
        try:
            device = Device.objects.get(id=device_id)
            device.status = 'offline'
            device.save()
            return device
        except Device.DoesNotExist:
            raise ObjectDoesNotExist(f"Device with ID {device_id} not found")