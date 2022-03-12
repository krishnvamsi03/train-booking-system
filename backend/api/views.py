from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status, request
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Train, Seats, SeatBookedTill, Coach, Station, Stops, CoachType, BookedSeat
import string
import random

"""user set of views"""


@api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def view_tickets(request: request) -> Response:
    if request.method == "GET":
        src, dest = Station.objects.filter(station_name=request.data["src"]).first(
        ), Station.objects.filter(station_name=request.data["dest"]).first()
        totalSeats = Seats.objects.filter(
            train__train_no=request.data["train_no"], coach__coach_name=request.data["coach_name"])
        bookedSeats = SeatBookedTill.objects.select_related('seat_id')
        if not bookedSeats:
            data = {}
            data["available seats"] = list(
                map(lambda x: x.__str__(), totalSeats))
            return Response({"available_seats": data}, status=status.HTTP_200_OK)
        else:
            filteredQuerySet = []
            for seats in bookedSeats:
                seatBookedFrom, seatBookedTill = Stops.objects.filter(station=seats.booked_from).first(
                ), Stops.objects.filter(station=seats.booked_till).first()
                srcBooking, destBooking = Stops.objects.filter(station=src).first(
                ), Stops.objects.filter(station=dest).first()
                if (srcBooking.train_stop_no >= seatBookedFrom.train_stop_no and srcBooking.train_stop_no < seatBookedTill.train_stop_no) or (destBooking.train_stop_no > seatBookedFrom.train_stop_no and destBooking.train_stop_no <= seatBookedTill.train_stop_no):
                    filteredQuerySet.append(seats.seat_id)
                elif (seatBookedFrom.train_stop_no >= srcBooking.train_stop_no and seatBookedFrom.train_stop_no <= destBooking.train_stop_no) or (seatBookedTill.train_stop_no >= srcBooking.train_stop_no and seatBookedTill.train_stop_no <= destBooking.train_stop_no):
                    filteredQuerySet.append(seats.seat_id)
            filteredQuerySet = list(map(lambda x: x.seat_id, filteredQuerySet))
            seats = totalSeats.exclude(seat_id__in=filteredQuerySet)
            data = {}
            data["available seats"] = list(
                map(lambda x: x.__str__(), seats))
            return Response(data, status=status.HTTP_200_OK)


def rollBackOperation(ticket, listOfSeats):
    ticket.delete()
    for seat in listOfSeats:
        seat.delete()


@api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def book_tickets(request: request) -> Response:
    if request.method == "POST":
        passengerDetails = request.data.get("passenger_details", None)
        srcStation, destStation = Station.objects.filter(
            station_name=request.data.get("src", None)).first(),
        destStation = Station.objects.filter(
            station_name=request.data.get("dest", None)).first()
        train = Train.objects.filter(
            train_no=request.data.get("train_no", None))
        coach = Coach.objects.filter(
            coach_name=request.data.get("coach_name", None), train=train)
        res = ''.join(random.choices(string.digits, k=10))
        ticket = TicketBooking(ticket_no=res, train=train, coach=coach,
                               src_station=srcStation, dest_station=destStation)
        listOfSeats = []
        if passengerDetails is not None:
            ticket.save()
            i = 0
            for details in passengerDetails:
                seat = Seats.objects.filter(train__train_no=request.data.get(
                    "train_no", None), coach__coach_name=request.data.get("coach_no", None).first(), seat_no=details.data.get("seat_no", None))
                if seat is None:
                    bookedSeat = SeatBookedTill.objects.filter(
                        seat_id=seat).filter()
                    if bookedSeat is not None:
                        bookedSrc, bookedDest = Stops.objects.filter(
                        ).first(), Stops.objects.filter().first()
                        src, dest = Stops.objects.filter().first(), Stops.objects.filter.first()
                        if (src.train_stop_no >= bookedSrc.train_stop_no and src.train_stop_no < bookedDest.train_stop_no) or (dest.train_stop_no > bookedSrc.train_stop_no and dest.train_stop_no <= bookedDest.train_stop_no):
                            rollBackOperation(ticket, listOfSeats)
                            return Response({"message": "given seat {} cannot be booked for given src and dest".format(seat.seat_no)}, status=status.HTTP_406_NOT_ACCEPTABLE)
                        elif (bookedSrc.train_stop_no >= src.train_stop_no and bookedSrc.train_stop_no <= dest.train_stop_no) or (bookedDest.train_stop_no >= src.train_stop_no and bookedDest.train_stop_no <= dest.train_stop_no):
                            rollBackOperation(ticket, listOfSeats)
                            return Response({"message": "given seat {} cannot be booked for given src and dest".format(seat.seat_no)}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    currSeat = BookedSeat.objects.create(ticket=ticket, seatNo=seat.seat_no, passengerName=details.data.get(
                        "passenger_name", "p" + str(i)))
                    unavailableSeat = SeatBookedTill.objects.create(
                        seat_id=currSeat, booked_from=srcStation, booked_till=destStation)
                    listOfSeats.append(unavailableSeat)
                else:
                    return Response({"message": "given seat no does not exist for train and coach"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "passenger or seat detail required"}, status=status.HTTP_400_BAD_REQUEST)
        pass


"""admin set of views"""


@api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def add_coach(request: request) -> Response:
    if request.method == "POST":
        try:
            train = Train.objects.filter(
                train_no=request.data.get("train_no", None)).first()
            coachType = CoachType.objects.filter(
                coach_type=request.data.get("coach_type")).first()
            if train is None or coachType is None:
                return Response({"message": "train or coach type is incorrect"}, status=status.HTTP_404_NOT_FOUND)
            coach = Coach.objects.create(coach_name=request.data.get(
                "coach_name", None), train=train, coach_type=coachType, available_seats=0)
            return Response({"message": "Successfully created coach", "coach id": coach.coach_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": "something went wrong! failed to create resource"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def remove_coach(request: request) -> Response:
    if request.method == "POST":
        coach = Coach.objects.filter(
            train__train_no=request.data["train_no"], coach_name=request.data["coach_name"]).first()
        if coach is not None:
            try:
                coach.delete()
                return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message: failed to find record"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def view_all_seats(request: request) -> Response:
    if request.method == "GET":
        totalSeats = Seats.objects.filter(
            train__train_no=request.data["train_no"], coach__coach_name=request.data["coach_name"])
        if totalSeats is not None:
            data = {}
            data["total_seats"] = list(map(lambda x: x.__str__(), totalSeats))
            return Response({"message": "success", "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "failed to find record", "data": ""}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def update_coach_details(request: request, coach_type: str) -> Response:
    if request.method == "PATCH":
        coach_type = CoachType.objects.filter(coach_type=coach_type).first()
        if coach_type is None:
            coach_type.coach_type = request.data.get(
                "coach_type", coach_type.coach_type)
            coach_type.coach_capacity = request.data.get(
                "coach_capacity", coach_type.coach_capacity)
            coach_type.save()
            return Response({"message": "Successfully updated resource"}, status=HTTP_200_OK)
        return Response({"message": "given coach not found"}, status=status.HTTP_404_NOT_FOUND)
