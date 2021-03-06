from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('home', views.edit_home, name=''),
    path('organiztion_information', views.edit_organiztion_information, name=''),
    path('golf', views.golf_view, name=''),
    path('edit-golf-<key>', views.edit_golf_classic_request, name=''),
    path('delete-golf-<key>', views.delete_golf_classic_request, name=''),
    path('new-golf', views.new_golf_classic_request, name=''),
    path('about_us', views.edit_about, name=''),
    path('people', views.edit_people, name=''),
    path('golf_registration', views.get_golf_registrations, name=''),
    path('donations', views.edit_donations, name=''),
    path('FAQ', views.edit_faq, name=''),
]