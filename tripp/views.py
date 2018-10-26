import math
from flask import request, make_response, jsonify
from sqlalchemy import or_, and_, func
from tripp import app, db
from models import *
from datetime import datetime


@app.route("/")
def hello():
    return 'Tripp says Hello!'


@app.route("/get-rooms", methods=['GET'])
def get_rooms():
    location = request.args.get('location')
    room_type = request.args.get('type')
    no_of_adults = int(request.args.get('adults'))
    no_of_children = int(request.args.get('children'))

    date_format = "%d-%m-%Y"
    check_in_time = datetime.strptime(request.args.get('checkInTime'), date_format)
    check_out_time = datetime.strptime(request.args.get('checkOutTime'), date_format)

    if check_out_time < check_in_time:
        return make_response(jsonify({"message": "Check in time greater than Check out time"})), 400

    no_of_people = no_of_adults + math.ceil(no_of_children)
    diff = check_out_time - check_in_time
    no_of_days = diff.days

    rooms = Room.query.filter(Room.location == location, Room.type == room_type).all()

    payload = []

    for room in rooms:
        is_available = False

        booked_rooms_count = Reservation.query.with_entities(func.sum(Reservation.no_of_rooms).label('no_of_rooms')) \
            .filter(Reservation.room_id == room.id,
                    or_(
                        and_((Reservation.check_out > check_in_time), (Reservation.check_in < check_in_time)),
                        and_(Reservation.check_out > check_out_time, Reservation.check_in < check_out_time),
                        and_(Reservation.check_in > check_in_time, Reservation.check_out < check_out_time)
                    )).first()

        available_rooms = 0

        if booked_rooms_count[0] is None:
            available_rooms = room.number_of_rooms
        elif booked_rooms_count[0] <= room.number_of_rooms:
            available_rooms = room.number_of_rooms - booked_rooms_count[0]

        available_capacity = available_rooms * room.capacity

        if available_capacity >= no_of_people:
            is_available = True

        if is_available:
            payload.append({
                "id": room.id,
                "location": room.location,
                "address": room.address,
                "type": room.type,
                "price": room.price * no_of_days,
                "capacity": room.capacity,
                "numberOfRooms": math.ceil(no_of_people / room.capacity)
            })

    if len(payload) > 0:
        return make_response(jsonify(payload)), 200
    else:
        return make_response(jsonify({"message": "Cannot accommodate in given type of room"})), 400


@app.route("/book", methods=['POST'])
def book():
    data = request.get_json()
    room_id = int(data.get("roomId"))
    customer_name = data.get("name")
    customer_email = data.get("email")
    customer_phone = data.get("phone")
    customer_card_details = data.get("cardDetails")
    number_of_rooms = int(data.get("rooms"))
    price = int(data.get("price"))

    date_format = "%d-%m-%Y"
    check_in_time = datetime.strptime(data.get('checkInTime'), date_format)
    check_out_time = datetime.strptime(data.get('checkOutTime'), date_format)

    new_reservation = Reservation(room_id=room_id, customer_name=customer_name, customer_email=customer_email,
                                  customer_phone=customer_phone, card_details=customer_card_details, price=price,
                                  no_of_rooms=number_of_rooms, check_in=check_in_time, check_out=check_out_time)

    db.session.add(new_reservation)
    db.session.commit()

    return make_response(jsonify({"message": "Reservation done successfully"})), 201
