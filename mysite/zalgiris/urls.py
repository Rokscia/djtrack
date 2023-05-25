from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views


app_name = 'zalgiris'

urlpatterns = [
    path("", views.index, name="index"),
    path("edit_score", views.edit_score, name="edit_score"),
    path("scores", views.scores, name="scores"),
]

urlpatterns += staticfiles_urlpatterns()
