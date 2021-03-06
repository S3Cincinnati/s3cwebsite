from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('our-team', views.our_team, name='Our Team'),
    path('golf-classic', views.get_golf_outing, name=''),
    path('golf-classic-sponsor', views.get_golf_outing_sponsorship, name=''),
    path('FAQ', views.get_faq, name=''),
    path('golf-classic-<year>/involvement', views.get_golf_outing_involvment_by_year, name=''),
    path('donate', views.get_donation, name=''),
    path('payment-succeed', views.my_webhook_view, name=''),
    path('stripe-webhook-paid/', views.stripe_webhook_paid_endpoint),
]