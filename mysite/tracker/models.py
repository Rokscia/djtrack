from django.db import models

# Create your models here.

class TrackerData(models.Model):
    timestamp = models.BigIntegerField(primary_key=True)
    date_time = models.DateTimeField(blank=False)
    latitude = models.FloatField(max_length=10, null=True)
    longitude = models.FloatField(max_length=10, null=True)
    ignition_status = models.BooleanField(null=True)
    movement_status = models.BooleanField(null=True)
    power_voltage = models.FloatField(max_length=10, null=True)
    battery_voltage = models.FloatField(max_length=10, null=True)
    can_engine_coolant_temp = models.IntegerField(null=True)
    can_engine_intake_air_temp = models.IntegerField(null=True)
    can_engine_rpm = models.IntegerField(null=True)
    can_engine_load_level = models.IntegerField(null=True)
    can_vehicle_speed = models.IntegerField(null=True)
    ble_temperature_1 = models.FloatField(max_length=8, null=True)
    ble_temperature_2 = models.FloatField(max_length=8, null=True)
    ble_humidity_1 = models.FloatField(max_length=8, null=True)
    ble_humidity_2 = models.FloatField(max_length=8, null=True)


    class Meta:
        ordering = ['timestamp'] # ['-timestamp'] for reverse ordering

    def get_nth_trip_coordinates(self, n):
        records = TrackerData.objects.order_by('-timestamp')
        # Iterate over all records to find the nth trip's coordinates
        trip_count = 0
        start_index = None
        end_index = None
        for i, record in enumerate(records):
            if record.ignition_status == 1:
                if start_index is None:
                    start_index = i
                else:
                    end_index = i
            if record.ignition_status == 0 and start_index is not None and end_index is not None:
                trip_count += 1
                if trip_count == n:
                    # Get the coordinates for this trip
                    trip_records = records[start_index:end_index+1]
                    coordinates = [[record.latitude, record.longitude] for record in trip_records]
                    return coordinates
                # Reset start and end index for next trip
                start_index = None
                end_index = None
        # If we reach here, it means we didn't find the nth trip
        return None


    def get_trip_data(self, trip_index):
        current_trip = None
        trip_count = 0
        for data in TrackerData.objects.filter(ignition_status=True):
            if not current_trip:
                current_trip = []
            current_trip.append(data)
            print(data)
            if not data.ignition_status:
                trip_count += 1
                if trip_count == trip_index:
                    return current_trip
                current_trip = None
        return None



