from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class Station(models.Model):
    station_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="Station ID")
    station_name = models.CharField(max_length=50, db_column="Name")
    no_of_platforms = models.IntegerField(db_column="No of platform")

    def __str__(self):
        return self.station_name


class Train(models.Model):
    train_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="Train ID")
    train_no = models.CharField(
        unique=True, max_length=5, db_column="Train No")
    train_name = models.CharField(max_length=50, db_column="Train Name")
    total_ac_coach = models.IntegerField(db_column="Total AC Coach")
    total_n_ac_coach = models.IntegerField(db_column="Total Non AC Coach")
    total_seater = models.IntegerField(db_column="Total Seats")
    src_station = models.ForeignKey(
        to=Station, related_name="%(class)s_src_station", on_delete=models.CASCADE, db_column="Source Station")
    dest_station = models.ForeignKey(
        to=Station, related_name="%(class)s_dest_staion", on_delete=models.CASCADE, db_column="Dest Station")

    def __str__(self):
        return self.train_name


class CoachType(models.Model):
    coach_type_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="Coach Type ID")
    coach_type = models.CharField(max_length=10, db_column="Coach Type")
    coach_capacity = models.IntegerField(db_column="Coach Capacity")

    def __str__(self):
        return self.coach_type


class Coach(models.Model):
    coach_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="Coach ID")
    coach_name = models.CharField(max_length=10, db_column="Coach Name")
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, db_column="Train")
    coach_type = models.ForeignKey(
        to=CoachType, on_delete=models.CASCADE, db_column="Coach Type")
    available_seats = models.IntegerField(db_column="Available Seats")

    def __str__(self):
        return self.coach_name


class Seats(models.Model):
    seat_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    seat_no = models.IntegerField(db_column="Seat No")
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, db_column="Train")
    coach = models.ForeignKey(
        to=Coach, on_delete=models.CASCADE, db_column="Coach")

    def __str__(self):
        return str(self.seat_no) + "-" + self.coach.coach_name + "-" + self.train.train_name


class SeatBookedTill(models.Model):
    seat_id = models.ForeignKey(to=Seats, on_delete=models.CASCADE)
    booked_from = models.ForeignKey(
        to=Station, on_delete=models.CASCADE, related_name="%(class)s_station_booked", db_column="Station Booked From")
    booked_till = models.ForeignKey(
        to=Station, on_delete=models.CASCADE, related_name="%(class)s_station_till", db_column="Station Booked Till")


class Stops(models.Model):
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, db_column="Train")
    station = models.ForeignKey(
        to=Station, on_delete=models.CASCADE, db_column="Station")
    train_stop_no = models.IntegerField(db_column="Train Stop No")

    def __str__(self):
        return self.station


class TicketBooking(models.Model):
    ticket_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    ticket_no = models.CharField(max_length=10)
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, db_column="Train")
    coach = models.ForeignKey(
        to=Coach, on_delete=models.CASCADE, db_column="Coach")
    src_station = models.ForeignKey(
        to=Station, on_delete=models.CASCADE, related_name="%(class)s_station_booked", db_column="Station Booked From")
    dest_station = models.ForeignKey(
        to=Station, on_delete=models.CASCADE, related_name="%(class)s_station_till", db_column="Station Booked Till")

    def __str__(self):
        return self.ticket_no


class BookedSeat(models.Model):
    ticket = models.ForeignKey(
        to=TicketBooking, on_delete=models.CASCADE, db_column="Ticket")
    seatNo = models.IntegerField(db_column="Seat No")
    passengerName = models.CharField(max_length=20, db_column="Passenger Name")

    def __str__(self):
        return self.seatNo + "-" + self.passengerName
