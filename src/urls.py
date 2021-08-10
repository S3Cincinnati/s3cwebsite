from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('golf-classic-<year>', views.get_golf_outing, name=''),
]