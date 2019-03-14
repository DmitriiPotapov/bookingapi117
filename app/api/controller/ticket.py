from flask_restplus import Resource, reqparse
from app.src.models import db, Ticket
from app.api.models.ticket import api, a_create_ticket, a_ticket_details
from app.api.models.ticket import a_approve_ticket
from app.src.helpers.decorators import token_required
from datetime import datetime, timedelta
from dateutil.parser import parse

errors = []
now = datetime.now()

@api.route('')
@api.response(404, 'Not Found')
class TicketApi(Resource):
    @api.doc(security=None, responses={200: 'Success',
                                       400: 'Bad Request' 
                                      })
    @api.marshal_list_with(a_ticket_details, envelope='flights')
    def get(self):
        flights = (Ticket.query.filter(Ticket.isArchived.is_(False))
                   .filter(Ticket.isExpired.is_(False))
                   .filter(Ticket.isPackaged.is_(False))
                   .filter(Ticket.isApproved.is_(True)).all())
        view_flights = []
        for flight in flights:
            view_flights.append(
                {
                    'id': flight.id,
                    'flightNo': flight.flightNo,
                    'origin': {
                        'location': flight.origin,
                        'date': flight.departureDate,
                        'time': flight.departureTime
                    },
                    'return': {
                        'location': flight.arrival,
                        'date': flight.returnDate,
                        'time': flight.returnTime
                    },
                    'remainingSlots': flight.remainingSlots,
                    'price': flight.price,
                    'expirationDate': flight.expirationDate,
                    'isExpired': flight.isExpired,
                    'isPackaged': flight.isPackaged,
                    'timestamp': {
                        'dateCreated': flight.dateCreated,
                        'dateUpdated': flight.dateUpdated
                    }
                }
            )
        return view_flights, 200
    
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.expect(a_create_ticket)
    def post(self):
        errors.clear()
        data = api.payload
        try:
            flight_number = data['flightNo']
            origin_location = data['origin']['location']
            origin_date = data['origin']['date']
            origin_time = data['origin']['time']
            return_location = data['return']['location']
            return_date = data['return']['date']
            return_time = data['return']['time']
            remaining_slots = data['remainingSlots']
            price = data['price']
            expiration_date = data['expirationDate']
            is_packaged = data['isPackaged']
            if data:
                if (not flight_number or
                        not origin_date or
                        not origin_location or
                        not origin_time or
                        not return_date or
                        not return_location or
                        not return_time or
                        not remaining_slots or
                        not price):
                    if not fight_number:
                        errors.append('Flight Number must not be null')
                    if not origin_date:
                        errors.append('Departure Date must not be null')
                    if not origin_location:
                        errors.append('Depature Location must not be null')
                    if not origin_time:
                        errors.append('Departure Time must not be null')
                    if not return_date:
                        errors.append('Return Date must not be null')
                    if not return_location:
                        errors.append('Return Location must not be null')
                    if not return_time:
                        errors.append('Return Time must not be null')
                    if not remaining_slots:
                        errors.append('Remaining Slots must not be null')
                    if not price:
                        errors.append('Price must not be null')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': errors}}, 400
                elif (parse(origin_date) <= now or 
                        parse(return_date) <= now or
                        parse(return_date) <= parse(origin_date) or
                        parse(expiration_date) <= now or
                        parse(expiration_date) >= parse(origin_date) or
                        int(remaining_slots) <= 0 or
                        float(price) <= 0 or
                        parse(expiration_date) >= parse(origin_date)):
                    if parse(origin_date) <= now:
                        errors.append('Departure date must not be less or equal '
                                      'to today\'s date')
                    if parse(return_date) <= now:
                        errors.append('Return date must not be less or equal '
                                      'to today\s date')
                    if parse(return_date) <= parse(origin_date):
                        errors.append('Return date must not be less or equal '
                                      'to departure date')
                    if int(remaining_slots) <= 0:
                        errors.append('Remaining slots must be greater than zero')
                    if float(price) <= 0:
                        errors.append('Price must be greater than zero')
                    if parse(expiration_date) <= now:
                        errors.append('Expiration date must be not be less ir equal '
                                      'to today\'s date')
                    if parse(expiration_date) >= parse(origin_date):
                        errors.append('Expiration date must not be greater or '
                                      'equal to departure date')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': errors}}, 400
                else:
                    new_ticket = Ticket(flightNo=flight_number,
                                        origin=origin_location,
                                        arrival=return_location,
                                        departureDate=origin_date,
                                        returnDate=return_date,
                                        departureTime=origin_time,
                                        returnTime=return_time,
                                        remainingSlots=remaining_slots,
                                        price=price,
                                        expirationDate=expiration_date,
                                        isPackaged=is_packaged)
                    db.session.add(new_ticket)
                    db.session.commit()
                    return {'message': 'Successfully added new ticket'}, 201
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.param('id', 'Ticket Id', 'query')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True,
                            help="Id must not be null", location='args')
        args = parser.parse_args()
        id = args['id']
        errors.clear()
        ticket = Ticket.query.get(id)
        if ticket:
            ticket.isArchived = True
            db.session.commit()
            return {'message': 'Successfully Archived'}, 200
        else:
            errors.append('Flight does not exist')
            return {'errors': {'status': 400,
                               'errorCode': 'E00F2',
                               'message': errors}}, 400

    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.param('id', 'Ticket Id', 'query')
    @api.expect(a_create_ticket)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()
        errors.clear()
        data = api.payload
        try:
            if args['id']:
                if args['id'].isdigit():
                    flight_number = data['flightNo']
                    origin_location = data['origin']['location']
                    origin_date = parse(data['origin']['date'])
                    origin_time = parse(data['origin']['time'])
                    return_location = data['return']['location']
                    return_date = parse(data['return']['date'])
                    return_time = parse(data['return']['time'])
                    remaining_slots = data['remainingSlots']
                    price = float(data['price'])
                    expiration_date = parse(data['expirationDate'])
                    is_packaged = data['isPackaged']
                    if data:
                        if (not flight_number or
                                not origin_date or
                                not origin_location or
                                not origin_time or
                                not return_date or
                                not return_location or
                                not return_time or
                                not remaining_slots or
                                not price):
                            if not flight_number:
                                errors.append('Flight Number must not be null')
                            if not origin_date:
                                errors.append('Departure Date must not be null')
                            if not origin_location:
                                errors.append('Depature Location must not be null')
                            if not origin_time:
                                errors.append('Departure Time must not be null')
                            if not return_date:
                                errors.append('Return Date must not be null')
                            if not return_location:
                                errors.append('Return Location must not be null')
                            if not return_time:
                                errors.append('Return Time must not be null')
                            if not remaining_slots:
                                errors.append('Remaining Slots must not be null')
                            if not price:
                                errors.append('Price must not be null')
                            return {'errors': {'status': 400,
                                            'errorCode': 'E0002',
                                            'message': errors}}, 400
                        elif (origin_date <= now or 
                                return_date <= now or
                                return_date <= origin_date or
                                expiration_date <= now or
                                expiration_date >= origin_date or
                                remaining_slots <= 0 or
                                price <= 0 or
                                expiration_date >= origin_date):
                            if origin_date <= now:
                                errors.append('Departure date must not be less or equal '
                                            'to today\'s date')
                            if return_date <= now:
                                errors.append('Return date must not be less or equal '
                                            'to today\s date')
                            if return_date <= origin_date:
                                errors.append('Return date must not be less or equal '
                                            'to departure date')
                            if remaining_slots <= 0:
                                errors.append('Remaining slots must be greater than zero')
                            if price <= 0:
                                errors.append('Price must be greater than zero')
                            if expiration_date <= now:
                                errors.append('Expiration date must be not be less ir equal '
                                            'to today\'s date')
                            if expiration_date >= origin_date:
                                errors.append('Expiration date must not be greater or '
                                            'equal to departure date')
                        else:
                            ticket = Ticket.query.get(args['id'])
                            if not ticket:
                                errors.append('Id not existing')
                                return {'errors': {'status': 400,
                                                'errorCode': 'E2002',
                                                'message': errors}}, 400
                            else:
                                ticket.flightNo = flight_number
                                ticket.origin = origin_location
                                ticket.departureDate = origin_date
                                ticket.departureTime = origin_time
                                ticket.arrival = return_location
                                ticket.returnDate = return_date
                                ticket.returnTime = return_time
                                ticket.remainingSlots = remaining_slots
                                ticket.price = price
                                ticket.expirationDate = expiration_date
                                ticket.isPackaged = is_packaged
                                db.session.commit()
                                return {'message': 'Successfully updated ticket'}, 200
                else:
                    errors.append('Parameter in the query string must be an integer')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E00F0',
                                       'message': errors}}, 400
            else:
                errors.append('Missing required parameter in the query string')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00F0',
                                   'message': errors}}, 400
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('/approval')
@api.response(404, 'Not Found')
@api.param('id', 'Ticket id', 'query')
class TicketApprovalApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                          400: 'Bad Request'})
    @token_required
    @api.expect(a_approve_ticket)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()
        errors.clear()
        data = api.payload
        try:
            if args['id']:
                if args['id'].isdigit():
                    ticket = Ticket.query.get(args['id'])
                    if ticket:
                        approve = data['isApproved']
                        ticket.isApproved = approve
                        db.session.commit()
                        if approve:
                            return {'message': "Successfully Approved"}, 200
                        else:
                            return {'message': "Ticket not Approved"}, 200
                    else:
                        errors.append('Ticket does no exist')
                        return {'errors': {'status': 400,
                                        'errorCode': 'E00F2',
                                        'message': errors}}, 400
                else:
                    errors.append('Parameter in the query string must be an integer')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E00F0',
                                       'message': errors}}, 400
            else:
                errors.append('Missing required parameter in the query string')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00F0',
                                   'message': errors}}, 400
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_ticket_details, envelope='flights')
    def get(self):
        flights = (Ticket.query.filter(Ticket.isArchived.is_(False))
                   .filter(Ticket.isExpired.is_(False))
                   .filter(Ticket.isPackaged.is_(False))
                   .filter(Ticket.isApproved.is_(False)).all())
        view_flights = []
        for flight in flights:
            view_flights.append(
                {
                    'id': flight.id,
                    'flightNo': flight.flightNo,
                    'origin': {
                        'location': flight.origin,
                        'date': flight.departureDate,
                        'time': flight.departureTime
                    },
                    'return': {
                        'location': flight.arrival,
                        'date': flight.returnDate,
                        'time': flight.returnTime
                    },
                    'remainingSlots': flight.remainingSlots,
                    'price': flight.price,
                    'expirationDate': flight.expirationDate,
                    'isExpired': flight.isExpired,
                    'isPackaged': flight.isPackaged,
                    'timestamp': {
                        'dateCreated': flight.dateCreated,
                        'dateUpdated': flight.dateUpdated
                    }
                }
            )
        return view_flights, 200

@api.route('/id=<int:id>')
@api.response(404, 'Not Found')
@api.param('id', 'Flight Id', 'query')
class TicketIdApi(Resource):
    @api.doc(security='apiKey', responses={200: "Success",
                                           400: "Bad Request"})
    @token_required
    def get(self, id):
        flight = (Ticket.query.filter(Ticket.isArchived.is_(False))
                  .filter(Ticket.isExpired.is_(False))
                  .filter(Ticket.id == id).first())
        if flight:
            view_flight = {
                            'id': flight.id,
                            'flightNo': flight.flightNo,
                            'origin': {
                                'location': flight.origin,
                                'date': flight.departureDate,
                                'time': flight.departureTime
                            },
                            'return': {
                                'location': flight.arrival,
                                'date': flight.returnDate,
                                'time': flight.returnTime
                            },
                            'remainingSlots': flight.remainingSlots,
                            'price': flight.price,
                            'expirationDate': flight.expirationDate,
                            'isExpired': flight.isExpired,
                            'isPackaged': flight.isPackaged,
                            'timestamp': {
                                'dateCreated': flight.dateCreated,
                                'dateUpdated': flight.dateUpdated
                            }
                        }
            return api.marshal(view_flight, a_ticket_details,
                               envelope='flight'), 200
        else:
            errors.append('Flight does not exist')
            return {'errors': {'status': 400,
                               'errorCode': 'E00F2',
                               'message': errors}}, 400
    