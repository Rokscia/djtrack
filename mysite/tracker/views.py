import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .models import TrackerData
from .forms import NameForm, ContactForm, NewUserForm
from .utils import update_tracker_data
from datetime import datetime


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("tracker:index")
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="tracker/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
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
    return render(request=request, template_name="tracker/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("tracker:index")


class IndexView(ListView):
    template_name = 'tracker/tracker.html'
    model = TrackerData
    context_object_name = 'latest_location_list'
    ordering = ['-timestamp']
    paginate_by = 5
    page_kwarg = 'trip_number'

    def get_context_data(self, **kwargs):
        update_tracker_data()
        context = super().get_context_data(**kwargs)
        trip_number = int(self.request.GET.get('trip_number', 1))
        data = TrackerData.objects.order_by('-timestamp').first()
        context['coordinates'] = data.get_nth_trip_coordinates(trip_number)
        context['location'] = data.latitude, data.longitude

        address_url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{data.longitude},{data.latitude}.json?limit=1&access_token={settings.MAPBOX_ACCESS_TOKEN}'
        response = requests.get(address_url)
        response_data = response.json()
        context['address'] = response_data['features'][0]['place_name']

        # Add links for previous and next trip
        prev_trip_number = max(1, trip_number - 1)
        next_trip_number = trip_number + 1
        context['prev_trip_url'] = f'?trip_number={prev_trip_number}'
        context['next_trip_url'] = f'?trip_number={next_trip_number}'

        return context


class CurrentLocationView(ListView):
    template_name = 'tracker/current_location.html'
    model = TrackerData
    context_object_name = 'latest_location_list'
    ordering = ['-timestamp']
    # paginate_by = 5
    # page_kwarg = 'trip_number'

    def get_context_data(self, **kwargs):
        update_tracker_data()
        context = super().get_context_data(**kwargs)
        # trip_number = int(self.request.GET.get('trip_number', 1))
        data = TrackerData.objects.order_by('-timestamp').first()
        # context['coordinates'] = data.get_nth_trip_coordinates(trip_number)
        context['location'] = data.latitude, data.longitude

        address_url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{data.longitude},{data.latitude}.json?limit=1&access_token={settings.MAPBOX_ACCESS_TOKEN}'
        response = requests.get(address_url)
        response_data = response.json()
        context['address'] = response_data['features'][0]['place_name']

        # Add links for previous and next trip
        # prev_trip_number = max(1, trip_number - 1)
        # next_trip_number = trip_number + 1
        # context['prev_trip_url'] = f'?trip_number={prev_trip_number}'
        # context['next_trip_url'] = f'?trip_number={next_trip_number}'

        return context

# def index(request):
#     create_tracker_data()
#     return HttpResponse('Data uploaded successfully')

# def last_location():
#     data = TrackerData.objects.order_by('-timestamp').first()
#     return data.latitude, data.longitude


# def index(request):
#     location = last_location()
#     return render(request, 'tracker/tracker.html', {"location": location})
