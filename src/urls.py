from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('our-team', views.our_team, name='Our Team'),
    path('golf-classic-<year>', views.get_golf_outing, name=''),
    path('golf-classic-<year>/involvement', views.get_golf_outing_involvment, name=''),
]