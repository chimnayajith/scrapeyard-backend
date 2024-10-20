from django.urls import path
from . import views

urlpatterns = [
    path('scrape-cars/', views.scrape_cars, name='scrape_cars'),
]
