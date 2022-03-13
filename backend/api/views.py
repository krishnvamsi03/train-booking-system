from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status, request
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Train, Seats, SeatBookedTill, Coach, Station, Stops, CoachType, BookedSeat, TicketBooking
import string
import random

"""user set of views"""


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def view_tickets(request: request) -> Response:
    """
    fetch availablity of seats for a train for src, dest
    """

    # check for in-valid request body.
    if request.method == "GET":
        if request.data.get("src", None) is None or \
                request.data.get("dest", None) is None or \
                request.data.get("train_no", None) is None or \
                request.data.get("coach_name", None) is None:
            return Response({"message": "invalid json, missing some data", "data": []}, status=status.HTTP_400_BAD_REQUEST)

        # Get source, destination station from DB
        src, dest = Station.objects.filter(station_name=request.data.get("src", None)).first(
        ), Station.objects.filter(station_name=request.data.get("dest", None)).first()

        # Fetch all seats for a train
        totalSeats = Seats.objects.filter(
            train__train_no=request.data.get("train_no", None), coach__coach_name=request.data.get("coach_name", None))

        # Fetch seats which are booked for this train
        bookedSeats = SeatBookedTill.objects.select_related('seat_id')
        data = {}
        if not bookedSeats:
            # If none of the seats for this train, return all seats
            data["available seats"] = list(
                map(lambda x: x.__str__(), totalSeats))
            return Response({"message": "accepted", "data": data}, status=status.HTTP_200_OK)
        else:
            # If some seats are booked, then check out of these seats if any seat are booked from and to station \
            # which is conflicting with user src, dest if yes remove all available seats
            filteredQuerySet = []
            for seats in bookedSeats:
                seatBookedFrom, seatBookedTill = Stops.objects.filter(station=seats.booked_from).first(
                ), Stops.objects.filter(station=seats.booked_till).first()
                srcBooking, destBooking = Stops.objects.filter(station=src).first(
                ), Stops.objects.filter(station=dest).first()

                # check for conflicts
                inWardConflict = (srcBooking.train_stop_no >= seatBookedFrom.train_stop_no and srcBooking.train_stop_no < seatBookedTill.train_stop_no) or (
                    destBooking.train_stop_no > seatBookedFrom.train_stop_no and destBooking.train_stop_no <= seatBookedTill.train_stop_no)
                outWardConflict = (seatBookedFrom.train_stop_no >= srcBooking.train_stop_no and seatBookedFrom.train_stop_no <= destBooking.train_stop_no) or (
                    seatBookedTill.train_stop_no >= srcBooking.train_stop_no and seatBookedTill.train_stop_no <= destBooking.train_stop_no)
                if inWardConflict or outWardConflict:
                    filteredQuerySet.append(seats.seat_id)

            # Get seat number for object
            filteredQuerySet = list(map(lambda x: x.seat_id, filteredQuerySet))
            # remove conflicted seats from total seats
            seats = totalSeats.exclude(seat_id__in=filteredQuerySet)
            data["available seats"] = list(
                map(lambda x: x.__str__(), seats))
            return Response({"message": "accepted", "data": data}, status=status.HTTP_200_OK)


def rollBackOperation(ticket, listOfSeats):
    """
    Helper function to deleted ticket, and seats
    """
    ticket.delete()
    for seat in listOfSeats:
        seat.delete()


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def book_tickets(request: request) -> Response:
    """
        Book ticket for user for src, dest of a particular train
    """
    if request.method == "POST":
        passengerDetails = request.data.get("passenger_details", None)

        # Basic null check for request body
        if request.data.get("src", None) is None or \
                request.data.get("dest", None) is None or \
                request.data.get("train_no", None) is None or \
                request.data.get("coach_name", None) is None:
            return Response({"message": "Invalid json object, some fields are missing", "data": ""}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch necessary info from db
        srcStation = Station.objects.filter(
            station_name=request.data.get("src", None)).first()
        destStation = Station.objects.filter(
            station_name=request.data.get("dest", None)).first()
        train = Train.objects.filter(
            train_no=request.data.get("train_no", None)).first()
        coach = Coach.objects.filter(
            coach_name=request.data.get("coach_name", None), train=train).first()
        # Generate random PNR number
        res = ''.join(random.choices(string.digits, k=10))
        # create Ticket object
        ticket = TicketBooking(ticket_no=res, train=train, coach=coach,
                               src_station=srcStation, dest_station=destStation, user=request.user)
        listOfSeats = []
        # Allocate seats for user if passenger details are correct and seats are available for src, dest
        if passengerDetails is not None:
            ticket.save()
            i = 0
            for details in passengerDetails:
                # Fetch the seat which user wants
                seat = Seats.objects.filter(train__train_no=request.data.get(
                    "train_no", None), coach__coach_name=request.data.get("coach_name", None), seat_no=details.get("seat_no", None)).first()
                if seat:
                    bookedSeats = SeatBookedTill.objects.filter(
                        seat_id=seat)
                    # check if seat is already booked or not
                    for bookedSeat in bookedSeats:
                        # if yes, check if from to station of this seat, so that it doest not conflict with user from to, if conflict, rollback all operations
                        bookedSrc, bookedDest = Stops.objects.filter(train=train, station=bookedSeat.booked_from
                                                                     ).first(), Stops.objects.filter(train=train, station=bookedSeat.booked_till).first()
                        src, dest = Stops.objects.filter(train=train, station=srcStation).first(
                        ), Stops.objects.filter(train=train, station=destStation).first()
                        # check for conflict
                        inWardConflict, outWardConflict = (src.train_stop_no >= bookedSrc.train_stop_no and src.train_stop_no < bookedDest.train_stop_no) or (dest.train_stop_no > bookedSrc.train_stop_no and dest.train_stop_no <= bookedDest.train_stop_no), (
                            bookedSrc.train_stop_no >= src.train_stop_no and bookedSrc.train_stop_no <= dest.train_stop_no) or (bookedDest.train_stop_no >= src.train_stop_no and bookedDest.train_stop_no <= dest.train_stop_no)
                        if inWardConflict or outWardConflict:
                            rollBackOperation(ticket, listOfSeats)
                            return Response({"message": "given seat {} cannot be booked for given src and dest".format(seat.seat_no)}, status=status.HTTP_406_NOT_ACCEPTABLE)

                    # if everything fine go ahead book ticket
                    print("book tickets")
                    currSeat = BookedSeat.objects.create(ticket=ticket, seatNo=seat.seat_no, passengerName=details.get(
                        "passenger_name", "p" + str(i)))
                    # make seat unavailable for next user
                    unavailableSeat = SeatBookedTill.objects.create(
                        seat_id=seat, booked_from=srcStation, booked_till=destStation)
                    listOfSeats.append(unavailableSeat)
                else:
                    return Response({"message": "given seat no {} does not exist for train and coach".format(details.get("seat_no", None))}, status=status.HTTP_400_BAD_REQUEST)
            data = {}
            data['ticket_no'] = ticket.ticket_no
            return Response({"message": "ticket booked successfully", "data": data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "passenger or seat detail required"}, status=status.HTTP_400_BAD_REQUEST)


"""admin set of views"""


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_coach(request: request) -> Response:
    """ 
    Add coach to a traine
    """
    if request.method == "POST":
        try:
            train = Train.objects.filter(
                train_no=request.data.get("train_no", None)).first()
            coachType = CoachType.objects.filter(
                coach_type=request.data.get("coach_type", None)).first()
            if train is None or coachType is None:
                return Response({"message": "train or coach type combination is not correct", "coach id": ""}, status=status.HTTP_404_NOT_FOUND)
            if request.data.get("coach_name", None) is None:
                return Response({"message": "coach name is required", "coach_id": ""}, status=status.HTTP_400_BAD_REQUEST)
            coach = Coach.objects.create(coach_name=request.data.get(
                "coach_name", None), train=train, coach_type=coachType, available_seats=0)
            return Response({"message": "Successfully created coach", "coach id": coach.coach_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": "something went wrong! failed to create resource", "coach id": ""}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def remove_coach(request: request, coach_name: str) -> Response:
    """Remove coach of a train"""
    if request.method == "DELETE":
        # get coach from db, or raise record not found error
        coach = Coach.objects.filter(
            train__train_no=request.data.get("train_no", None), coach_name=coach_name).first()
        if coach is not None:
            try:
                coach.delete()
                return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message: failed to find record"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def view_all_seats(request: request) -> Response:
    """
    View all seat of a train
    """
    if request.method == "GET":
        totalSeats = Seats.objects.filter(
            train__train_no=request.data.get("train_no", None), coach__coach_name=request.data.get("coach_name", None))
        if totalSeats:
            data = {}
            # retrive seat from object
            data["total_seats"] = list(map(lambda x: x.__str__(), totalSeats))
            return Response({"message": "success", "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "failed to find record", "data": ""}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_coach_details(request: request, coach_type: str) -> Response:
    """
    update coach details
    """
    if request.method == "PUT":
        coach_type = CoachType.objects.filter(coach_type=coach_type).first()
        if coach_type:
            coach_type.coach_type = request.data.get(
                "coach_type", coach_type.coach_type)
            coach_type.coach_capacity = request.data.get(
                "coach_capacity", coach_type.coach_capacity)
            coach_type.save()
            return Response({"message": "Successfully updated resource"}, status=HTTP_200_OK)
        return Response({"message": "given coach not found"}, status=status.HTTP_404_NOT_FOUND)
