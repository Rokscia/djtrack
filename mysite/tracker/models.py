from django.db import models
from django.core.cache import cache
from datetime import datetime


class TripMetadata(models.Model):
    trip_index = models.IntegerField(primary_key=True)
    start_timestamp = models.BigIntegerField()
    end_timestamp = models.BigIntegerField()

    class Meta:
        ordering = ["trip_index"]

    def get_start_end_timestamps(self):
        first_record = (
            TrackerData.objects.filter(trip=self).order_by("timestamp").first()
        )
        last_record = (
            TrackerData.objects.filter(trip=self).order_by("-timestamp").first()
        )
        if first_record and last_record:
            return first_record.timestamp, last_record.timestamp
        else:
            return None, None

    @classmethod
    def get_times_for_trip(cls, trip_index):
        try:
            trip_metadata = cls.objects.get(trip_index=trip_index)
            start_datetime = datetime.fromtimestamp(trip_metadata.start_timestamp)
            end_datetime = datetime.fromtimestamp(trip_metadata.end_timestamp)
            duration = end_datetime - start_datetime
            return (str(start_datetime), str(end_datetime), str(duration))
        except cls.DoesNotExist:
            return None, None


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
    segment_mileage = models.FloatField(null=True)
    trip = models.ForeignKey(TripMetadata, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["timestamp"]  # ['-timestamp'] for reverse ordering

    @classmethod
    def get_data_in_trip(cls, trip_index):
        try:
            trip_metadata = TripMetadata.objects.get(trip_index=trip_index)
            start_timestamp, end_timestamp = trip_metadata.get_start_end_timestamps()
            data_in_range = cls.get_data_in_range(start_timestamp, end_timestamp)
            return data_in_range
        except TripMetadata.DoesNotExist:
            return None

    @classmethod
    def get_data_in_range(cls, start_timestamp, end_timestamp):
        try:
            return cls.objects.filter(
                timestamp__gte=start_timestamp, timestamp__lte=end_timestamp
            )
        except TypeError:
            return None

    @classmethod
    def get_nth_trip_top_speed(cls, n):
        trip_records = cls.get_data_in_trip(n)
        top_speed = 0
        for record in trip_records:
            if record.can_vehicle_speed is None:
                continue
            if record.can_vehicle_speed > top_speed:
                top_speed = record.can_vehicle_speed
        return top_speed

    @classmethod
    def get_nth_trip_distance(cls, n):
        trip_records = cls.get_data_in_trip(n)
        if trip_records:
            last_record = trip_records.last()
            distance = (
                last_record.segment_mileage
                if last_record.segment_mileage is not None
                else 0.0
            )
            return round(distance, 2)
        else:
            return 0.0

    def get_nth_trip_data(self, n):
        # Check if the result is already cached
        cache_key = f"nth_trip_data_{n}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        records = TrackerData.objects.order_by("-timestamp")
        trip_count = 0
        start_index = None
        end_index = None
        for i, record in enumerate(records):
            if record.ignition_status == 1:
                if start_index is None:
                    start_index = i
                else:
                    end_index = i
            if (
                record.ignition_status == 0
                and start_index is not None
                and end_index is not None
            ):
                trip_count += 1
                if trip_count == n:
                    # Get the records for this trip
                    trip_records = records[start_index : end_index + 1]
                    # Store the result in the cache
                    cache.set(cache_key, trip_records)
                    return trip_records
                # Reset start and end index for next trip
                start_index = None
                end_index = None
        # If we reach here, it means we didn't find the nth trip
        return None

    def delete_nth_trip_data(self, n: int):
        self.clear_trip_cache()  # Clear the entire cache
        # Delete the trip records
        try:
            trip_metadata = TripMetadata.objects.get(trip_index=n)
            trip_metadata.delete()
            return True, f"Successfully deleted the {n}th trip."
        except TripMetadata.DoesNotExist:
            return False, f"No records found for the {n}th trip."

    @staticmethod
    def clear_trip_cache():
        cache.clear()  # Clear the entire cache

    def get_nth_trip_coordinates(self, n):
        trip_records = self.get_nth_trip_data(n)
        if trip_records:
            coordinates = [
                [record.latitude, record.longitude] for record in trip_records
            ]
            return coordinates
        else:
            return None

    def get_coordinates_for_date_range(start_timestamp, end_timestamp):
        trip_records = TrackerData.get_data_in_range(start_timestamp, end_timestamp)
        if trip_records:
            coordinates = [
                [record.latitude, record.longitude] for record in trip_records
            ]
            return coordinates
        else:
            return None

    def get_trip_data(self, trip_index):
        current_trip = None
        trip_count = 0
        for data in TrackerData.objects.filter(ignition_status=True):
            if not current_trip:
                current_trip = []
            current_trip.append(data)
            if not data.ignition_status:
                trip_count += 1
                if trip_count == trip_index:
                    return current_trip
                current_trip = None
        return None
