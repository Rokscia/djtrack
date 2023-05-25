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
]

urlpatterns += staticfiles_urlpatterns()
