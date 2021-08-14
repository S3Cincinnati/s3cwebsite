"""s3cwebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from src.views import createSessionCheckoutView, my_webhook_view

urlpatterns = [
    path('', include('src.urls')),
    path('admin/', include('custAdmin.urls')),
    path('developer-admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # new,
    path('create-checkout-session-view-<year>', createSessionCheckoutView.as_view(), name='create-checkout-session-view'),
    path('webhook',my_webhook_view, name='webhook')
]
