from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# User Models
class User(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    firstName = db.Column("FirstName", db.String(50))
    middleName = db.Column("MiddleName", db.String(50))
    lastName = db.Column("LastName", db.String(50))
    email = db.Column("Email", db.String(100))
    # username = db.Column("Username", db.String(50))
    password_hashed = db.Column("Password", db.String(250))
    role = db.Column("Role", db.String(25))
    publicId = db.Column("PublicId", db.String(255))
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now(),
                            default=db.func.now())
    isArchived = db.Column('IsArchived', db.Boolean, default=False)
    isAuthenticated = db.Column('IsAuthenticated', db.Boolean, default=False)
    hotelBooking = db.relationship("HotelBooking", backref='User',
                                   lazy=True)
    flightBooking = db.relationship("FlightBooking", backref='User',
                                    lazy=True)
    packageBooking = db.relationship("PackageBooking", backref='User',
                                     lazy=True)

    __tablename__ = 'users'


# Log In Trail
class LogTrail(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    event = db.Column("Event", db.String(250))
    eventTime = db.Column("EventTime", db.DateTime, default=db.func.now())

    __tablename__ = "logtrails"


# Tickets Model
class Ticket(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    flightNo = db.Column("FlightNo", db.String(100))
    origin = db.Column("Origin", db.String(100))
    arrival = db.Column("Arrival", db.String(100))
    departureDate = db.Column("DepartureDate", db.Date)
    departureTime = db.Column("DepartureTime", db.Time)
    returnDate = db.Column("ReturnDate", db.Date)
    returnTime = db.Column("ReturnTime", db.Time)
    remainingSlots = db.Column("RemainingSlots", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    price = db.Column('Price', db.Float(asdecimal=True))
    isExpired = db.Column("IsExpired", db.Boolean, default=False)
    isPackaged = db.Column("IsPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now(),
                            default=db.func.now())
    isArchived = db.Column('IsArchived', db.Boolean, default=False)
    isApproved = db.Column('IsApproved', db.Boolean, default=False)
    ticketBooking = db.relationship("FlightBooking", backref='Flight',
                                    lazy=True)
    packageFlight = db.relationship('Package', backref='Tickets', lazy=True)

    __tablename__ = "tickets"

    def __repr__(self):
        return '{} ({} - {})'.format(self.flightNo,
                                     self.origin,
                                     self.arrival)


# Hotel Model
class Hotel(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(250))
    roomType = db.Column("Room Type", db.String(250))
    capacity = db.Column("Capacity", db.Integer())
    details = db.Column("Details", db.String(300))
    checkIn = db.Column("CheckIn", db.Date)
    checkOut = db.Column("CheckOut", db.Date)
    price = db.Column('Price', db.Float(asdecimal=True))
    expirationDate = db.Column("ExpirationDate", db.Date)
    isExpired = db.Column("IsExpired", db.Boolean, default=False)
    isPackaged = db.Column("IsPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now(),
                            default=db.func.now())
    remainingRooms = db.Column('RemainingRooms', db.Integer)
    isArchived = db.Column('IsArchived', db.Boolean, default=False)
    isApproved = db.Column('IsApproved', db.Boolean, default=False)
    hotelBooking = db.relationship("HotelBooking", backref='Hotel',
                                   lazy=True)
    packageHotel = db.relationship('Package', backref='Hotels', lazy=True)

    __tablename__ = "hotels"

    def __repr__(self):
        return '{} ({})'.format(self.name,
                                self.roomType)


# Customer Model
class Customer(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    firstName = db.Column("FirstName", db.String(250))
    lastName = db.Column("LastName", db.String(250))
    email = db.Column("Email", db.String(100))
    contactNo = db.Column("Contact", db.String(50))
    isArchived = db.Column('IsArchived', db.Boolean, default=False)

    __tablename__ = "customers"

    def __repr__(self):
        return '{} {} ({})'.format(self.firstName,
                                   self.lastName,
                                   self.email)


# Flight Inquiry
class FlightInquiry(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('users.Id'))
    origin = db.Column("Origin", db.String(100))
    arrival = db.Column("Arrival", db.String(100))
    departureDate = db.Column("DepartureDate", db.Date)
    arrivalDate = db.Column("ArrivalDate", db.Date)
    time = db.Column("DesiredTime", db.String(100))
    adult = db.Column("NumberOfAdults", db.Integer)
    child = db.Column("NumberOfChild", db.Integer)
    infant = db.Column("NumberOfInfant", db.Integer)
    note = db.Column("Note", db.String(300))
    isArchived = db.Column('IsArchived', db.Boolean, default=False)

    __tablename__ = "flightinquiries"


# Hotel Inquiry
class HotelInquiry(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('users.Id'))
    location = db.Column("Location", db.String(100))
    budget = db.Column("Budget", db.Float(asdecimal=True))
    guest = db.Column("Guest", db.Integer)
    checkIn = db.Column("checkInDate", db.Date)
    checkOut = db.Column("checkOutDate", db.Date)
    note = db.Column("Note", db.String(300))
    isArchived = db.Column('IsArchived', db.Boolean, default=False)

    __tablename__ = "hotelinquiries"


# Package
class Package(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    destination = db.Column("Destination", db.String(50))
    price = db.Column('Price', db.Float(asdecimal=True))
    days = db.Column("DaysOfStay", db.Integer)
    intenerary = db.Column("Intenerary", db.String(1000))
    inclusions = db.Column("Inclusions", db.String(1000))
    remainingSlots = db.Column("RemainingSlots", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    note = db.Column("Note", db.String(1000))
    hotel = db.Column('HotelsFk', db.Integer, db.ForeignKey('hotels.Id'))
    flight = db.Column('FlightFk', db.Integer, db.ForeignKey('tickets.Id'))
    isArchived = db.Column('IsArchived', db.Boolean, default=False)
    isExpired = db.Column('isExpired', db.Boolean, default=False)
    isApproved = db.Column('IsApproved', db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now(),
                            default=db.func.now())
    packageBooking = db.relationship("PackageBooking", backref='Package',
                                     lazy=True)

    __tablename__ = 'packages'

    def __repr__(self):
        return '{}'.format(self.destination)


# Package Boooking
class PackageBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('users.Id'))
    package = db.Column('PackagesFk', db.Integer, db.ForeignKey('packages.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'packagebookings'


# Hotel Booking
class HotelBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('users.Id'))
    hotel = db.Column('HotelsFk', db.Integer, db.ForeignKey('hotels.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'hotelbookings'


# Flight Booking
class FlightBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('users.Id'))
    flight = db.Column('FlightFk', db.Integer, db.ForeignKey('tickets.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'ticketbookings'


# Strip Customer
class StripeCustomer(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    email = db.Column("Email", db.String(50))
    stripeCustomerId = db.Column("StripeCustomerId", db.String(50))

    __tablename__ = 'stripcustomers'


# Payments
class Payments(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    paymentReference = db.Column("PaymentReference", db.String(50))
    bookingReference = db.Column("BookingReference", db.String(50))
    paymentFor = db.Column("PaymentFor", db.String(50))
    stripeCustomer = db.Column("StripeCustomer",
                               db.ForeignKey('stripcustomers.Id'))
    stripeChargeId = db.Column("StripChargeId", db.String(50))

    __tablename__ = "payments"
