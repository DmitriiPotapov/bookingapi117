from flask import request
from flask_restplus import Resource
from app.src.models import db, User, HotelInquiry, FlightInquiry
from app.src.helpers.decorators import token_required, token_details
from app.api.models.inquiry import api, a_inquiries_flight_details, a_inquiries_hotel_details
from app.api.models.inquiry import a_inquiries_hotel_create, a_inquiries_flight_create
from datetime import datetime
from dateutil.parser import parse

errors = []
now = datetime.now()

@api.route('/tickets')
@api.response(404, 'Not Found')
class TicketInquiry(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_inquiries_flight_details, envelope='flight')
    def get(self):
        ticket_inquiry = FlightInquiry.query.all()
        view_ticket_inquiry = []
        for ticket in ticket_inquiry:
            user = User.query.get(ticket.customer)
            view_ticket_inquiry.append(
                {
                    'id': ticket.id,
                    'customer': {
                        'id': user.id,
                        'name': {
                            'first': user.firstName,
                            'middle': user.middleName,
                            'last': user.lastName
                        },
                        'email': user.email
                    },
                    'flight': {
                        'origin': {
                            'location': ticket.origin,
                            'date': ticket.departureDate
                        },
                        'departure': {
                            'location': ticket.arrival,
                            'date': ticket.arrivalDate
                        }
                    },
                    'passenger': {
                        'adult': ticket.adult,
                        'child': ticket.child,
                        'infant': ticket.infant
                    },
                    'note': ticket.note
                }
            )
        return view_ticket_inquiry, 200

    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.expect(a_inquiries_flight_create)
    def post(self):
        errors.clear()
        data = api.payload
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        try:
            flight_details = data['flight']
            origin = flight_details['origin']['location']
            departure = flight_details['departure']['location']
            origin_date = flight_details['origin']['date']
            departure_date = flight_details['departure']['date']
            passenger = data['passenger']
            adults = passenger['adult']
            child = passenger['child']
            infant = passenger['infant']
            note = data['note']
            if (not origin or
                    not departure or
                    not origin_date or
                    not departure_date or
                    # not adults or
                    # not child or
                    # not infant or
                    not note):
                if not origin:
                    errors.append('Origin must not be null')
                if not departure:
                    errors.append('Departure must not be null')
                if not origin_date:
                    errors.append('Origin Date must not be null')
                if not departure_date:
                    errors.append('Departure Date must not be null')
                if not adults:
                    errors.append('Adult count must not be null')
                if not infant:
                    errors.append('Infant count must not be null')
                if not child:
                    errors.append('Children count must not be null')
                if not note:
                    errors.append('Note must not be null')
                return {'errors': {'status': 400,
                                   'errorsCodes': 'E00I2',
                                   'message': errors}}, 400
            if (parse(origin_date) < now or
                    parse(departure_date) < now or
                    parse(departure_date) < parse(origin_date) or
                    int(adults) < 0 or
                    int(child) < 0 or
                    int(infant) < 0):
                return {'errors': {'status': 400,
                                   'errorsCodes': 'E00I2',
                                   'message': errors}}, 400
            else:
                new_inquiry = FlightInquiry(customer=user.id,
                                            origin=origin,
                                            arrival=departure,
                                            departureDate=parse(origin_date),
                                            arrivalDate=parse(departure_date),
                                            adult=int(adults),
                                            child=int(child),
                                            infant=int(infant),
                                            note=note)
                db.session.add(new_inquiry)
                db.session.commit()
                return {'message': 'Successfully Submitted a Ticket Inquiry'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400


@api.route('/hotels')
@api.response(404, 'Not Found')
class HotelInquiryApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_inquiries_hotel_details, envelope="hotels")
    def get(self):
        hotel_inquiry = HotelInquiry.query.all()
        view_hotel = []
        for hotel in hotel_inquiry:
            user = User.query.get(hotel.customer)
            view_hotel.append(
                {
                    'id': hotel.id,
                    'customer': {
                        'id': user.id,
                        'name': {
                            'first': user.firstName,
                            'middle': user.middleName,
                            'last': user.lastName
                        },
                        'email': user.email
                    },
                    'hotel': {
                        'location': hotel.location,
                        'budget': hotel.budget
                    },
                    'checkDates': {
                        'in': hotel.checkIn,
                        'out': hotel.checkOut
                    },
                    'guestNumber': hotel.guest,
                    'note': hotel.note
                }
            )
        return view_hotel, 200


    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.expect(a_inquiries_hotel_create)
    def post(self):
        errors.clear()
        data = api.payload
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId == token['sub']).first()
        try:
            hotel_details = data['hotel']
            location = hotel_details['location']
            budget = hotel_details['budget']
            check_dates = data['checkDates']
            check_in = check_dates['in']
            check_out = check_dates['out']
            guest_number = data['guestNumber']
            note = data['note']
            if (not location or
                    not budget or
                    not check_in or
                    not check_out or
                    not guest_number):
                if not location:
                    errors.append('Location must not be null')
                if not budget:
                    errors.append('Budget must not be null')
                if not check_in:
                    errors.append('Check in date must not be null')
                if not check_out:
                    errors.append('Check out date must not be null')
                if not guest_number:
                    errors.append('Guest Number must not be null')
                return {'errors': {'status': 400,
                                   'errorCodes': 'E00I2',
                                   'message': errors}}, 400
            if (parse(check_in) <= now or
                    parse(check_out) <= now or
                    parse(check_out) <= parse(check_in) or
                    float(budget) <= 0):
                if parse(check_in) <= now:
                    errors.append('Check in date must be greater than the date today')
                if parse(check_out) <= now:
                    errors.append('Check out date must be greater than the date today')
                if parse(check_out) <= parse(check_in):
                    errors.append('Check out date must not be higher than the check in date')
                if float(budget) < 1:
                    errors.append('Budget must be greater than 0')
                return {'errors': {'status': 400,
                                   'errorCodes': 'E00I2',
                                   'message': errors}}, 400
            else:
                new_inquiry = HotelInquiry(customer=user.id,
                                           location=location,
                                           budget=budget,
                                           checkIn=parse(check_in),
                                           checkOut=parse(check_out),
                                           guest=guest_number,
                                           note=note)
                db.session.add(new_inquiry)
                db.session.commit()
                return {'message': 'Successfully submitted a Hotel Inquiry'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400
        