from tripp import db


class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200))
    type = db.Column(db.String(200))
    capacity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __repr__(self):
        return self.location + " " + self.type


class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(200))
    customer_phone = db.Column(db.String(20))
    card_details = db.Column(db.String(200))

    room = db.relationship('Room', backref='reservation')

    def __repr__(self):
        return str(self.room_id) + " " + self.customer_name
