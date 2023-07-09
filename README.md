# djtrack - Car Tracker Data Visualization

This application retrieves data from a Teltonika FMB003 car tracker via the flespi server API and visualizes it using a Django web application.

## Features

- Retrieves car tracker data from the flespi server API
- Stores the data in a database for easy access
- Provides a web interface to view and analyze the car tracker data
- Integrates with Bootstrap 4 for responsive and visually appealing UI

## Usage

- On the home page, you will see the latest trip's track on the map, trip's data on the right and below you will find four charts with trip's data.
  -  Use the navigation buttons (<<, PREVIOUS TRIP, NEXT TRIP, >>) to navigate between trips.
  -  Registered/logged in user can also delete trips one by one.
- A list of available trips retrieved from the car tracker is available on the TRIPS LIST page.
  - Click on a trip row to view the details of that trip.
  - The trips are paginated, and you can use the pagination navigation at the bottom to switch between pages.
- LAST PARKING LOCATION page displays the latest received coordinate of the tracked vehicle.

## Acknowledgements

This project was created as the final project for the CodeAcademy Python Programming course by Rokas Kanapienis. It demonstrates the skills and knowledge acquired during the course.

I would like to express my gratitude to CodeAcademy for providing the educational resources and guidance throughout the course. Special thanks to the teacher Viktoras Pranckietis for his valuable support and mentorship.
