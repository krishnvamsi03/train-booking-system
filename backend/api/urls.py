from django.urls import path
from . import views

urlpatterns = [
    path('get_availability', view=views.view_tickets, name="availability"),
    path('book_ticket', view=views.book_tickets, name="book"),
    path('add_coach', view=views.add_coach, name="add coach"),
    path('remove_coach/<str:coach_name>', view=views.remove_coach, name="remove coach"),
    path('view_all_seats', view=views.view_all_seats, name="view all seats"),
    path('update_coach/<str:coach_type>',
         view=views.update_coach_details, name="update coach")
]
