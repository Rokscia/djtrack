import requests
from .models import TrackerData
from django.conf import settings
from datetime import datetime


json_response_field_mapping = {
    'position.latitude': 'latitude',
    'position.longitude': 'longitude',
    'engine.ignition.status': 'ignition_status',
    'movement.status': 'movement_status',
    'external.powersource.voltage': 'power_voltage',
    'battery.voltage': 'battery_voltage',
    'can.engine.coolant.temperature': 'can_engine_coolant_temp',
    'can.intake.air.temperature': 'can_engine_intake_air_temp',
    'can.engine.rpm': 'can_engine_rpm',
    'can.engine.load.level': 'can_engine_load_level',
    'can.vehicle.speed': 'can_vehicle_speed',
    'ble.sensor.temperature.1': 'ble_temperature_1',
    'ble.sensor.temperature.2': 'ble_temperature_2',
    'ble.sensor.humidity.1': 'ble_humidity_1',
    'ble.sensor.humidity.2': 'ble_humidity_2',
}


def update_tracker_data():
    last_timestamp_in_db = TrackerData.objects.order_by(
        '-timestamp').first().timestamp
    url = f'https://flespi.io/gw/devices/5065494/messages?data=%7B%22from%22%3A{last_timestamp_in_db}%7D'
    response = requests.get(url, headers={
                            'Authorization': 'FlespiToken bA7wjMXBPjs6UlyJdfxOu3vStY8ACnTENP0XpNm4UEZDPlcRqxtKoOrHAp73CPvd'})
    data = response.json()

    for item in data['result']:
        timestamp = item['timestamp']

        if TrackerData.objects.filter(timestamp=timestamp).exists():
            continue

        date_time = datetime.fromtimestamp(item['timestamp'])
        tracker_data = TrackerData(timestamp=timestamp, date_time=date_time)
        for json_field, db_column in json_response_field_mapping.items():
            setattr(tracker_data, db_column, item.get(json_field, None))

        tracker_data.save()

    return print('TrackerData updated successfully')
