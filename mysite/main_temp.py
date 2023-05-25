from tracker.models import TrackerData

last_timestamp = TrackerData.objects.order_by('-timestamp').first().timestamp

print(last_timestamp)