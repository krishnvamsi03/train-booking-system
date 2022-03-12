from django.urls import path
from . import views

urlpatterns = [
    path('get_availability', view=views.view_tickets, name="availability"),
]
