from rest_framework.views import APIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .models import Device, Event
from .serializers import DeviceSerializer, EventSerializer
from .services import EventService

# Device Management with APIView
class DeviceAPIView(APIView):
    """
    API view for managing devices.

    Methods:
        get(request, pk=None): Retrieve a device by its ID or list all devices.
        post(request): Create a new device.
        put(request, pk=None): Update a device by its ID.
        delete(request, pk=None): Delete a device by its ID.
        post_activate(request, pk=None): Activate a device by its ID.
        post_deactivate(request, pk=None): Deactivate a device by its ID.
    
    Sample queries:
    - Get all devices: 
        GET /devices/
    - Get a specific device: 
        GET /devices/{id}/
    - Create a new device: 
        POST /devices/ 
        { "name": "Device 1", "type": "temperature_sensor", "location": "Room 101" }
    - Update a device:
        PUT /devices/{id}/ 
        { "name": "Updated Device" }
    - Delete a device:
        DELETE /devices/{id}/
    - Activate a device:
        POST /devices/{id}/activate/
    - Deactivate a device:
        POST /devices/{id}/deactivate/
    """
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 

    def get_queryset(self):
        """
        Return the queryset of devices.
        """
        return Device.objects.all()
    
    def get(self, request, pk=None):
        """
        Retrieve a specific device by its ID or list all devices.
        
        Parameters:
            request: The HTTP request object.
            pk: Primary key of the device (optional).
        
        Returns:
            Response: A JSON representation of the device(s) or an error message.
        """
        if pk:
            try:
                device = Device.objects.get(pk=pk)
                serializer = DeviceSerializer(device)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Device.DoesNotExist:
                return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            devices = Device.objects.all()
            serializer = DeviceSerializer(devices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new device.

        Sample request payload:
        {
            "name": "Temperature Sensor 1",
            "device_id": "sensor_12345",
            "status": "online",
            "location": "Room 101",
            "configuration": {
                "threshold": 25.5,
                "unit": "Celsius"
            }
        }

        Fields:
        - name (required): Name of the device (string, max length 100).
        - device_id (required): Unique identifier for the device (string, max length 100).
        - status (optional): Status of the device ('online', 'offline'). Defaults to 'offline'.
        - location (optional): Location of the device (string).
        - configuration (optional): JSON field to store device-specific configurations.
        
        Returns:
            - 201 Created: If the device is successfully created.
            - 400 Bad Request: If the request data is invalid.
        """
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """
        Update an existing device by its ID.

        Parameters:
            request: The HTTP request object containing updated device data.
            pk: Primary key of the device to be updated.
        
        Returns:
            Response: A JSON representation of the updated device or an error message.
        """
        try:
            device = Device.objects.get(pk=pk)
            serializer = DeviceSerializer(device, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        """
        Delete an existing device by its ID.

        Parameters:
            request: The HTTP request object.
            pk: Primary key of the device to be deleted.
        
        Returns:
            Response: A 204 No Content status if the device was successfully deleted, 
                      or a 404 Not Found status if the device does not exist.
        """
        try:
            device = Device.objects.get(pk=pk)
            device.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

    def post_activate(self, request, pk=None):
        """
        Activate a specific device by its ID.

        Parameters:
            request: The HTTP request object.
            pk: Primary key of the device to be activated.
        
        Returns:
            Response: A success message or an error message.
        """
        try:
            device = EventService.activate_device(pk)
            return Response({'status': f'Device {device.name} activated'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post_deactivate(self, request, pk=None):
        """
        Deactivate a specific device by its ID.

        Parameters:
            request: The HTTP request object.
            pk: Primary key of the device to be deactivated.
        
        Returns:
            Response: A success message or an error message.
        """
        try:
            device = EventService.deactivate_device(pk)
            return Response({'status': f'Device {device.name} deactivated'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Endpoint to receive events
class EventCreateAPIView(APIView):
    """
    API view to create new events for devices.

    Methods:
        post(request): Create a new event and store it in the database.

    Sample query:
    - Create a new event:
        POST /events/ 
        { "device_id": 1, "temperature": 22.5, "event_time": "2023-09-18T12:00:00Z" }
    """
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 
    queryset = Device.objects.all() 
    def post(self, request):
        """
        Create a new event for a device.

        Parameters:
            request: The HTTP request object containing event data.
        
        Returns:
            Response: A JSON representation of the created event or an error message.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Query events by device and date range
class EventListAPIView(APIView):
    """
    API view to list events for a specific device within a date range.

    Methods:
        get(request): Retrieve events for a specific device between the given dates.

    Sample query:
    - Get events for a device between a date range:
        GET /events/list/?device_id=1&start_date=2023-09-01&end_date=2023-09-15
    """
    def get_queryset(self):
        """
        Return the queryset of devices.
        """
        return Event.objects.all()
    
    def get(self, request):
        """
        List events for a specific device within a date range.

        Parameters:
            request: The HTTP request object.
        
        Returns:
            Response: A JSON representation of the event(s) or an error message.
        """
        device_id = request.query_params.get('device_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not device_id or not start_date or not end_date:
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        events = Event.objects.filter(device_id=device_id, event_time__range=[start_date, end_date])
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Query summary report
class EventSummaryAPIView(APIView):
    """
    API view to get a summary report of events (max, min, and average temperature)
    for a specific device and date range.

    Methods:
        get(request): Retrieve summary statistics (max, min, avg temperature) 
                      for a specific device within the given dates.

    Sample query:
    - Get a summary report for a device between a date range:
        GET /events/summary/?device_id=1&start_date=2023-09-01&end_date=2023-09-15
    """
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 
    
    def get_queryset(self):
        """
        Return the queryset of devices.
        """
        return Event.objects.all()
    
    def get(self, request):
        """
        Get the summary of events (max, min, avg temperature) for a specific device 
        within a date range.

        Parameters:
            request: The HTTP request object.
        
        Returns:
            Response: A JSON representation of the summary statistics or an error message.
        """
        device_id = request.query_params.get('device_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not device_id or not start_date or not end_date:
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        events = Event.objects.filter(device_id=device_id, event_time__range=[start_date, end_date])
        summary = events.aggregate(
            max_temp=models.Max('temperature'),
            min_temp=models.Min('temperature'),
            avg_temp=models.Avg('temperature')
        )
        return Response(summary, status=status.HTTP_200_OK)
