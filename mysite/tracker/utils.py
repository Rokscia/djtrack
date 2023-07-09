import requests
from .models import TrackerData, TripMetadata
from django.conf import settings
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.io as pio


json_response_field_mapping = {
    "position.latitude": "latitude",
    "position.longitude": "longitude",
    "engine.ignition.status": "ignition_status",
    "movement.status": "movement_status",
    "external.powersource.voltage": "power_voltage",
    "battery.voltage": "battery_voltage",
    "can.engine.coolant.temperature": "can_engine_coolant_temp",
    "can.intake.air.temperature": "can_engine_intake_air_temp",
    "can.engine.rpm": "can_engine_rpm",
    "can.engine.load.level": "can_engine_load_level",
    "can.vehicle.speed": "can_vehicle_speed",
    "ble.sensor.temperature.1": "ble_temperature_1",
    "ble.sensor.temperature.2": "ble_temperature_2",
    "ble.sensor.humidity.1": "ble_humidity_1",
    "ble.sensor.humidity.2": "ble_humidity_2",
    "segment.vehicle.mileage": "segment_mileage",
}


def update_tracker_data():
    try:
        last_timestamp_in_db = (
            TrackerData.objects.order_by("-timestamp").first().timestamp
        )
        url = f"https://flespi.io/gw/devices/5065494/messages?data=%7B%22from%22%3A{last_timestamp_in_db}%7D"
        response = requests.get(
            url,
            headers={
                "Authorization": "FlespiToken bA7wjMXBPjs6UlyJdfxOu3vStY8ACnTENP0XpNm4UEZDPlcRqxtKoOrHAp73CPvd"
            },
        )

        # Raise an exception for error status codes
        response.raise_for_status()
        data = response.json()

        for item in data["result"]:
            timestamp = item["timestamp"]

            if TrackerData.objects.filter(timestamp=timestamp).exists():
                continue

            date_time = datetime.fromtimestamp(item["timestamp"])
            tracker_data = TrackerData(timestamp=timestamp, date_time=date_time)
            for json_field, db_column in json_response_field_mapping.items():
                setattr(tracker_data, db_column, item.get(json_field, None))

            tracker_data.save()

        TrackerData.clear_trip_cache()

        update_trip_metadata(last_timestamp_in_db)

        return "TrackerData updated successfully"
    except Exception as e:
        return f"Error occurred: {str(e)}"


def update_trip_metadata(last_timestamp_before_update):
    records = TrackerData.objects.filter(
        timestamp__gt=last_timestamp_before_update
    ).order_by("timestamp")
    trip_count = TripMetadata.objects.order_by("-trip_index").first().trip_index
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

            trip_metadata = TripMetadata(
                trip_index=trip_count,
                start_timestamp=records[start_index].timestamp,
                end_timestamp=records[end_index].timestamp,
            )
            trip_metadata.save()

            # Update the trip field for the records of the current trip
            for trip_record in records[start_index : end_index + 1]:
                trip_record.trip = trip_metadata
                trip_record.save()

            # Reset start and end index for the next trip
            start_index = None
            end_index = None

    # Create trip metadata for the last trip if necessary
    if start_index is not None and i == len(records) - 1:
        trip_count += 1

        trip_metadata = TripMetadata(
            trip_index=trip_count,
            start_timestamp=records[start_index].timestamp,
            end_timestamp=records[i].timestamp,
        )
        trip_metadata.save()

        # Update the trip field for the records of the last trip
        for trip_record in records[start_index:]:
            trip_record.trip = trip_metadata
            trip_record.save()


def get_trip_coordinates(trip_index):
    trip_records = TrackerData.get_data_in_trip(trip_index)
    if trip_records:
        coordinates = [[record.latitude, record.longitude] for record in trip_records]
        return coordinates
    else:
        return None


def get_address(coordinates: list):
    address_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{coordinates[1]},{coordinates[0]}.json?limit=1&access_token={settings.MAPBOX_ACCESS_TOKEN}"
    response = requests.get(address_url)
    response_data = response.json()
    return response_data["features"][0]["place_name"]


def get_dataframes(n):
    trip_records = TrackerData.get_data_in_trip(n)

    # Convert TrackerData objects to dictionaries
    trip_data = []
    for trip in trip_records:
        trip_data.append(
            {
                "date_time": trip.date_time,
                "can_vehicle_speed": trip.can_vehicle_speed,
                "ble_temperature_1": trip.ble_temperature_1,
                "can_engine_coolant_temp": trip.can_engine_coolant_temp,
                "can_engine_rpm": trip.can_engine_rpm,
            }
        )

    # Create a DataFrame from the converted trip data
    df = pd.DataFrame(trip_data)
    return df


def get_graph(n, y_column, title, yaxis_title):
    df = get_dataframes(n)

    # Plotting the graph
    fig = px.line(df, x="date_time", y=y_column)
    fig.update_layout(title=title, xaxis_title="Date and Time", yaxis_title=yaxis_title)

    # Convert the Plotly graph to HTML
    graph_html = pio.to_html(fig, full_html=False)
    return graph_html


# UPDATE ONLY SEGMENT MILEAGE FOR EXISTING TIMESTAMPS
# def update_tracker_data():
#     try:
#         url = f'https://flespi.io/gw/devices/5065494/messages?data=%7B%22fields%22%3A%22timestamp%2Csegment.vehicle.mileage%22%2C%22filter%22%3A%22segment.vehicle.mileage%3E0%22%2C%22from%22%3A1681310000%7D'
#         response = requests.get(url, headers={
#             'Authorization': 'FlespiToken bA7wjMXBPjs6UlyJdfxOu3vStY8ACnTENP0XpNm4UEZDPlcRqxtKoOrHAp73CPvd'})
#         response.raise_for_status()  # Raise an exception for non-2xx status codes
#         data = response.json()

#         for item in data['result']:
#             timestamp = item['timestamp']
#             mileage = item['segment.vehicle.mileage']

#             try:
#                 tracker_data = TrackerData.objects.get(timestamp=timestamp)
#                 tracker_data.segment_mileage = mileage
#                 tracker_data.save()
#             except TrackerData.DoesNotExist:
#                 continue

#         TrackerData.clear_trip_cache()

#         return 'TrackerData updated successfully'
#     except Exception as e:
#         return f'Error occurred: {str(e)}'
