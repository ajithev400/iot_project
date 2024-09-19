from rest_framework import serializers
from .models import Device, Event
from django.utils import timezone

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

    def validate_device_id(self, value):
        """
        Validate that the device_id is unique.
        """
        if Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("A device with this device_id already exists.")
        return value

    def validate_status(self, value):
        """
        Validate that the status is either 'online' or 'offline'.
        """
        if value not in ['online', 'offline']:
            raise serializers.ValidationError("Invalid status. Must be 'online' or 'offline'.")
        return value

    def validate_configuration(self, value):
        """
        Validate that the configuration is a valid JSON object with necessary fields.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Configuration must be a valid JSON object.")
        
        # Example of checking for specific fields in the configuration
        if 'threshold' in value:
            if not isinstance(value['threshold'], (int, float)):
                raise serializers.ValidationError("Threshold must be a number.")
        
        return value

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['device', 'temperature', 'event_time']

    def validate_device(self, value):
        """
        Validate that the device exists and is active.
        """
        if value.status != 'online':
            raise serializers.ValidationError(f"Device {value.name} is currently offline.")
        return value

    def validate_temperature(self, value):
        """
        Validate that the temperature is within a reasonable range.
        """
        if value < -50 or value > 150:  # Example range -50°C to 150°C
            raise serializers.ValidationError("Temperature must be between -50 and 150 degrees Celsius.")
        return value

    def validate_event_time(self, value):
        """
        Ensure the event time is not in the future.
        """
        
        if value > timezone.now():
            raise serializers.ValidationError("Event time cannot be in the future.")
        return value