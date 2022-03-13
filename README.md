# train-booking-system

Requirements
User Requirements

1. User can view all available seats
2. User can book available seat for specific coach of a train
3. User is allowed to book multiple seats.
4. User can book seats available
5. Assumption, User will select seats of his choice. System will not take care of seat assignment

Admin Requirements

1. Admin is allowed to add extra coaches to train, and coaches can be any one of these (AC, Non/AC, seater)
2. Similarly, Admin can remove coaches of train.
3. View all available seats and non available seats of specific coach of a train.
4. Update details of coach of train (Not clear, exactly what kind of details admin is supposed to update)

DB Schema

<img width="766" alt="image" src="https://user-images.githubusercontent.com/50523101/158023305-ff264c73-b7d1-42e3-be29-9591547d67d6.png">

1. User Table
   User table is will contain user details like name, email, and isAdmin and other details

2. Station
   Station table will be responsible for station name, and other meta data of station.

3. Train
   Train table will be responsible for Train related queries, it contains train_no, name, no of coach in each category

4. Coach Type
   This table will contain three different type of coaches, AC, NAC, SC so in future if any new coach come we need to change here. this table will also contain coach capacity

5. Coach
   This table will be have foreign key of Train to know which train it belong and coach type for knowing type of coach

6. Seats
   This table will contain all the seats of specific coachs of a train

7. SeatBookedTill
   This table will help us in letting know availability of seats, if user wants to know availability of seats from A to B, we can query this table for availibility
   this will be having lookup to seat, and src and destination station

8. Stops
   This table will hold all the stations and specific train will be travelling, it contain train no (FK), station (FK), stop_no: (order in which this stop will come 1 2 3 ..)
   this will help us in letting availbility of seats, for if seat booked from A to E, and user want availability of D to H, we don't know E comes first or D comes first, this table will help in that

9. TicketBooking
   This table will contain train, ticket, seats details

10. Seat booked
    This table will be having lookup to above tables and seat detail, as for one ticket we can have multiple seats this will store multiple seat info

Attached detailed schema of system as html file,

Please add these header for respective set of apis and also attached sample request body
Header for User apis
Key: Authorization
Value: Token 850506ba1131f4d7c7b75e44d24c5750ee2ebddd

Admin
Key: Authorization
Value: Token b5cd99a79b778a576958fc65af1f8d8b169f980d

User Set of views
```json
1. "http://localhost:8000/api/get_availability"

GET: Request body
Sample
{
    "train_no": "12908",
    "coach_name": "AC1",
    "src": "Station B",
    "dest": "Station G"
}

2. "http://localhost:8000/api/book_ticket"
POST: request body
book ticket
{
    "train_no": "12908",
    "coach_name": "AC1",
    "src": "Station G",
    "dest": "Station H",
    "passenger_details": [
        {
            "passenger_name": "p11",
            "seat_no": 12
        },
        {
            "passenger_name": "p12",
            "seat_no": 13
        }
    ]
}
```

Admin set of Request

```json
View: "Remove coach: "http://localhost:8000/api/view_all_seats"
GET
1. View all seats
{
    "train_no": "",
    "coach_name": "",
}

Add coach: "http://localhost:8000/api/add_coach"
POST
2. add Coach
{
    "train_no": "12908",
    "coach_name": "AC4", 
    "coach_type": "AC Coach"
}

Remove coach: "http://localhost:8000/api/remove_coach/AC4{you can use this from previous api}"
DELETE
3. remove coach
{
    "train_no": "12908"
}

update: "Remove coach: "http://localhost:8000/api/update_coach/<str:coach_type>"
coach Type: "AC, NAC, SC"
4. update coach
{
    "coach_type": "",
    "coach_capacity": 50,
}

```

Didn't get a chance to test application, if any doubt please reach out to me \n
github repo: https://github.com/krishnvamsi03/train-booking-system/
