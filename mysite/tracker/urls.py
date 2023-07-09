from django.urls import path
from tracker import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


app_name = 'tracker'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path("current_location", views.CurrentLocationView.as_view(), name="current_location"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path("update_tracker_data", views.UpdateTrackerData.as_view(), name="update_tracker_data"),
    path("delete_nth_trip", views.delete_nth_trip, name="delete_nth_trip"),
    path("calendar", views.CalendarView.as_view(), name="calendar"),
    path('trip_list', views.TripListView.as_view(), name='trip_list'),
]

urlpatterns += staticfiles_urlpatterns()
