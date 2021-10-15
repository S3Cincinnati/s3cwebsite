from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('home', views.edit_home, name=''),
    path('golf', views.golf_view, name=''),
    path('edit-golf-<key>', views.edit_golf_classic_request, name=''),
    path('new-golf', views.new_golf_classic_request, name=''),
    path('about_us', views.edit_about, name=''),
    path('people', views.edit_people, name=''),
]