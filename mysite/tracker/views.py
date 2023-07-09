from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic import TemplateView, ListView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views import View
from django.urls import reverse
from django.core.paginator import Paginator

from .models import TrackerData, TripMetadata
from .forms import NewUserForm
from .utils import update_tracker_data, get_address, get_graph, get_trip_coordinates
from datetime import datetime, date, timedelta


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("tracker:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(
        request=request,
        template_name="tracker/register.html",
        context={"register_form": form},
    )


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("tracker:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request,
        template_name="tracker/login.html",
        context={"login_form": form},
    )


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("tracker:index")


# Homepage View (Trips)
class IndexView(TemplateView):
    template_name = "tracker/tracker.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve all trip indexes in a list
        trip_indexes_list = list(
            TripMetadata.objects.values_list("trip_index", flat=True)
        )
        last_trip_number = trip_indexes_list[-1]
        context["last_trip_number"] = last_trip_number

        # Retrieve the requested trip number from the URL parameter, defaulting to the last trip number
        trip_number = int(self.request.GET.get("trip_number", last_trip_number))

        # Check if the requested trip number is valid
        if trip_number not in trip_indexes_list:
            # Return a 404 error if the requested trip number does not exist
            raise Http404("Trip not found")

        context["trip_number"] = trip_number
        context["coordinates"] = get_trip_coordinates(trip_number)
        (
            context["start_address"],
            context["end_address"],
        ) = self.get_start_and_end_addresses(context["coordinates"])
        context["times"] = TripMetadata.get_times_for_trip(trip_number)
        context["top_speed"] = TrackerData.get_nth_trip_top_speed(trip_number)
        context["distance"] = TrackerData.get_nth_trip_distance(trip_number)

        # Add the graphs HTML to the context
        context["speed_graph_html"] = get_graph(
            trip_number, "can_vehicle_speed", "Vehicle Speed Graph", "Vehicle Speed"
        )
        context["temp_graph_html"] = get_graph(
            trip_number,
            "ble_temperature_1",
            "Interior Temperature Graph",
            "Interior Temperature",
        )
        context["coolant_temp_graph_html"] = get_graph(
            trip_number, "can_engine_coolant_temp", "Coolant Temp Graph", "Coolant Temp"
        )
        context["engine_rpm_graph_html"] = get_graph(
            trip_number, "can_engine_rpm", "Engine RPM Graph", "Engine RPM"
        )

        # Get the previous and next trip numbers for pagination
        prev_trip_number, next_trip_number = self.get_previous_and_next_trip_numbers(
            trip_indexes_list, trip_number
        )
        context["prev_trip_url"] = self.get_trip_url(prev_trip_number)
        context["next_trip_url"] = self.get_trip_url(next_trip_number)

        return context

    def get_start_and_end_addresses(self, coordinates):
        if coordinates:
            start_address = get_address(coordinates[0])
            end_address = get_address(coordinates[-1])
            return start_address, end_address
        return None, None

    def get_previous_and_next_trip_numbers(self, trip_indexes_list, trip_number):
        current_index = trip_indexes_list.index(trip_number)
        prev_trip_number = (
            trip_indexes_list[current_index - 1] if current_index > 0 else None
        )
        next_trip_number = (
            trip_indexes_list[current_index + 1]
            if current_index < len(trip_indexes_list) - 1
            else None
        )
        return prev_trip_number, next_trip_number

    def get_trip_url(self, trip_number):
        # Generate the trip URL if the trip number exists
        if trip_number is not None:
            return f"?trip_number={trip_number}"
        return None


class TripListView(ListView):
    model = TripMetadata
    template_name = "tracker/trip_list.html"
    paginate_by = 20
    context_object_name = "trip_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip_indexes_list = list(
            TripMetadata.objects.values_list("trip_index", flat=True)
        )
        last_trip_number = trip_indexes_list[-1]
        trip_number = int(self.request.GET.get("trip_number", last_trip_number))

        if trip_number not in trip_indexes_list:
            raise Http404("Trip not found")

        trip_data_list = []
        for trip_index in reversed(trip_indexes_list):
            start_datetime, end_datetime, _ = TripMetadata.get_times_for_trip(
                trip_index
            )
            distance = TrackerData.get_nth_trip_distance(trip_index)
            trip_data = {
                "Trip_ID": trip_index,
                "Start_datetime": start_datetime,
                "End_datetime": end_datetime,
                "Distance": distance,
            }
            trip_data_list.append(trip_data)

        paginator = Paginator(trip_data_list, self.paginate_by)
        page_number = self.request.GET.get("page")
        trip_list = paginator.get_page(page_number)

        context["trip_list"] = trip_list

        return context


class CalendarView(View):
    template_name = "tracker/calendar.html"

    def get(self, request):
        date_range = request.GET.get("date_range")

        if date_range:
            # Parse the date range string
            start_date_str, end_date_str = date_range.split(" - ")
            start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
            end_date = datetime.strptime(end_date_str, "%m/%d/%Y") + timedelta(days=1)
        else:
            # Handle the case when no date range is selected
            today = date.today()
            start_date = datetime.combine(today, datetime.min.time()) - timedelta(
                days=6
            )
            end_date = start_date + timedelta(days=7)

        # Convert the start and end dates to timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        coordinates = TrackerData.get_coordinates_for_date_range(
            start_timestamp, end_timestamp
        )

        if coordinates is None:
            coordinates = []
        # Create the context dictionary and add the desired data
        context = {
            "coordinates": coordinates,
            "start_date": start_date,
            "end_date": end_date,
        }

        return render(
            request=request, template_name="tracker/calendar.html", context=context
        )


def delete_nth_trip(request):
    if request.method == "POST":
        trip_number = int(request.POST.get("trip_number"))
        data = TrackerData.objects.order_by("-timestamp").first()
        success, message = data.delete_nth_trip_data(trip_number)
        if success:
            messages.info(request, message)
        else:
            messages.error(request, message)

    # Retrieve the list of trip indexes
    trip_indexes = TripMetadata.objects.values_list("trip_index", flat=True).order_by(
        "trip_index"
    )

    # Get the index of the next trip
    next_trip_index = trip_indexes.filter(trip_index__gt=trip_number).first()
    if next_trip_index is not None:
        trip_url = reverse("tracker:index") + f"?trip_number={next_trip_index}"
    else:
        # Redirect to the index page if there is no next trip
        trip_url = reverse("tracker:index")

    return redirect(trip_url)


class UpdateTrackerData(View):
    def get(self, request):
        result = update_tracker_data()
        messages.info(request, result)
        return redirect("tracker:index")


class CurrentLocationView(TemplateView):
    template_name = "tracker/current_location.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = TrackerData.objects.order_by("-timestamp").first()
        context["location"] = data.latitude, data.longitude

        context["address"] = get_address([data.latitude, data.longitude])
        return context
