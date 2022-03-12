from django.contrib import admin
from .models import Station, Train, CoachType, Coach, Seats, SeatBookedTill, Stops, TicketBooking, BookedSeat
# Register your models here.


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Station._meta.fields]


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Train._meta.fields]


@admin.register(CoachType)
class CoachTypeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CoachType._meta.fields]


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Coach._meta.fields]


@admin.register(Seats)
class SeatsAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Seats._meta.fields]


@admin.register(SeatBookedTill)
class SeatBookedTillAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SeatBookedTill._meta.fields]


@admin.register(Stops)
class StopsAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Stops._meta.fields]


@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TicketBooking._meta.fields]


@admin.register(BookedSeat)
class BookedSeatAdmin(admin.ModelAdmin):
    list_display = [f.name for f in BookedSeat._meta.fields]
