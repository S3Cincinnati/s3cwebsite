from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('new-golf', views.new_golf_classic_request, name='')
]