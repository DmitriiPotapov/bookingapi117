from flask import request
from flask_restplus import Resource
from app.src.models import db, PackageBooking, HotelBooking, FlightBooking
from app.src.models import User, Ticket, Hotel, Package
from app.src.helpers.decorators import token_required, token_details, referenceNumber
from app.api.models.booking import api, a_ticket_booking_details, a_hotel_booking_details
from app.api.models.booking import a_package_booking_details, a_ticket_booking
from app.api.models.booking import a_hotel_booking, a_package_booking
from datetime import datetime
from dateutil.parser import parse

errors = []

@api.route('/ticket')
@api.response(404, 'Not Found')
class TicketBookingApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.marshal_list_with(a_ticket_booking_details, envelope='tickets')
    def get(self):
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        tickets = FlightBooking.query.filter(FlightBooking.customer==user.id).all()
        view_tickets = []
        for ticket in tickets:
            packaged_ticket = Ticket.query.get(ticket.flight)
            view_tickets.append(
                {
                    'id': ticket.id,
                    'referenceNumber': ticket.referenceNumber,
                    'ticket': {
                        'id': ticket.flight,
                        'flightNo': packaged_ticket.flightNo,
                        'origin': {
                            'location': packaged_ticket.origin,
                            'date': packaged_ticket.departureDate,
                            'time': packaged_ticket.departureTime
                        },
                        'return': {
                            'location': packaged_ticket.arrival,
                            'date': packaged_ticket.returnDate,
                            'time': packaged_ticket.returnTime
                        },
                        'remainingSlots': packaged_ticket.remainingSlots,
                        'price': packaged_ticket.price,
                        'expirationDate': packaged_ticket.expirationDate
                    },
                    'isPaid': ticket.isPaid,
                    'status': ""
                }
            )
        return view_tickets, 200

    @api.doc(security='apiKey', responses={201: 'Created',
                                           400: 'Bad Request'})
    @token_required
    @api.expect(a_ticket_booking)
    def post(self):
        errors.clear()
        data = api.payload
        ticket = int(data['ticket'])
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        try:
            if not ticket:
                errors.append('Ticket must not be null')
                return {'errors': {'status': 400,
                                   'errorCode': 'E0002',
                                   'message': errors}}, 400
            else:
                new_booking = FlightBooking(referenceNumber='TBK' + referenceNumber,
                                            customer=user.id,
                                            flight=ticket)
                ticket = Ticket.query.get(ticket)
                ticket.remainingSlots = ticket.remainingSlots - 1
                db.session.add(new_booking)
                db.session.commit()
                return {'message': 'You have successfully booked a ticket'}
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('/hotel')
@api.response(404, 'Not Found')
class HotelBookingApi(Resource):
    @api.doc(security='apiKey',
             responses={200: 'Success',
                        400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_hotel_booking_details, envelope='hotels')
    def get(self):
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        hotel_bookings = HotelBooking.query.filter(HotelBooking.customer==user.id).all()
        print(hotel_bookings)
        view_hotels = []
        for hotel in hotel_bookings:
            packaged_hotel = Hotel.query.get(hotel.hotel)
            view_hotels.append(
                {
                    'id': hotel.id,
                    'referenceNumber': hotel.referenceNumber,
                    'hotel': {
                        'id': packaged_hotel.id,
                        'name': packaged_hotel.name,
                        'room': {
                            'type': packaged_hotel.roomType,
                            'capacity': packaged_hotel.capacity
                        },
                        'details': packaged_hotel.details,
                        'checkDates': {
                            'in': packaged_hotel.checkIn,
                            'out': packaged_hotel.checkOut
                        },
                        'price': packaged_hotel.price,
                        'expirationDate': packaged_hotel.expirationDate,
                        'remainingRooms': packaged_hotel.remainingRooms
                    },
                    'isPaid': hotel.isPaid
                }
            )
        return view_hotels, 200

    @api.doc(security='apiKey', responses={201: 'Created',
                                           400: 'Bad Request'})
    @token_required
    @api.expect(a_hotel_booking)
    def post(self):
        errors.clear()
        data = api.payload
        hotel = int(data['hotel'])
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        try:
            if not hotel:
                errors.append('Hotel must not be null')
                return {'errors': {'status': 400,
                                   'errorCode': 'E0002',
                                   'message': errors}}, 400
            else:
                new_booking = HotelBooking(referenceNumber='HBK' + referenceNumber,
                                           customer=user.id,
                                           hotel=hotel)
                hotel = Hotel.query.get(hotel)
                hotel.remainingRooms = hotel.remainingRooms - 1
                db.session.add(new_booking)
                db.session.commit()
                return {'message': 'You have successfully booked a Hotel'}
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('/package')
@api.response(404, 'Not Found')
class PackageBookingApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_package_booking_details)
    def get(self):
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(user.publicId==token['sub']).first()
        bookings = PackageBooking.query.filter(PackageBooking.customer==user.id).all()
        view_packages = []
        for booking in bookings:
            package = Package.query.get(booking.package)
            ticket = Ticket.query.get(package.flight)
            hotel = Hotel.query.get(package.hotel)
            view_packages.append(
                {
                    'id': booking.id,
                    'referenceNumber': booking.referenceNumber,
                    'package': {
                        'id': package.id,
                        'details': {
                            'days': package.days,
                            'itinerary': package.intenerary,
                            'inclusions': package.inclusions,
                            'notes': package.note
                        },
                        'price': package.price,
                        'ticket': {
                            'id': ticket.id,
                            'flightNo': ticket.flightNo,
                            'origin': ticket.origin,
                            'departure': ticket.arrival
                        },
                        'hotel': {
                            'id': hotel.id,
                            'name': hotel.name,
                            'roomType': hotel.roomType,
                            'capacity': hotel.capacity
                        },
                        'remainingSlots': package.remainingSlots,
                        'expirationDate': package.expirationDate
                    },
                    'isPaid': booking.isPaid
                }
            )
        return view_packages, 200
        
    @api.doc(security='apiKey', responses={201: 'Created',
                                           400: 'Bad Request'})
    @token_required
    @api.expect(a_package_booking)
    def post(self):
        errors.clear()
        data = api.payload
        package = int(data['package'])
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        try:
            if not package:
                errors.append('Package must not be null')
                return {'errors': {'status': 400,
                                   'errorsCode': 'E0002',
                                   'message': errors}}
            else:
                new_booking = PackageBooking(referenceNumber='PBK' + referenceNumber,
                                             customer=user.id,
                                             package=package)
                package = Package.query.get(package)
                package.remainingSlots = package.remainingSlots - 1
                db.session.add(new_booking)
                db.session.commit()
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400