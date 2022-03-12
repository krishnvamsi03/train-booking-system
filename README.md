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

User
view available seats in coach
{
    train_no: "",
    coach_name: "",
    src: "src_station_name",
    dest: "dest_station_name",
}

book ticket
{
    user_id: "",
    train_no: "",
    coach_name: "",
    src: "",
    dest: "",
    passenger_details: [
        {
            "passenger_name": "name",
            "seat_no": 2
        },
        {
            "passenger_name": "name",
            "seat_no": 3
        }
    ]
}

Admin set of Request
1. View all seats
{
    train_no: "",
    coach_no: "",
}

2. add Coach
{
    train_no: "",
    coach_name: "",
    coach_type: ""
}

3. remove coach
{
    train_no: "",
    coach_name: ""
}

4. update coach
{
    "coach_type": "",
    "coach_capacity": 50,
}