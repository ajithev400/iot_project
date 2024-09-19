from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline')], default='offline')
    location = models.CharField(max_length=200, null=True, blank=True)  # Location of the device
    configuration = models.JSONField(default=dict, null=True, blank=True)  # Store device-specific configurations
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='events')
    temperature = models.FloatField()
    event_time = models.DateTimeField()  # Time when the event occurred

    class Meta:
        ordering = ['-event_time']  

    def __str__(self):
        return f"{self.device.name} - {self.temperature}°C at {self.event_time}"