from flask_restplus import Resource, reqparse
from app.src.models import db, Package, Hotel, Ticket
from app.api.models.package import api, a_package_details, a_create_package
from app.api.models.package import a_archive_package, a_approve_package
from app.api.models.package import a_hotel_details, a_ticket_details
from app.src.helpers.decorators import token_required
from datetime import datetime, timedelta
from dateutil.parser import parse

errors = []
now = datetime.now()

@api.route('')
@api.response(404, 'Not Found')
class PackageApi(Resource):
    @api.doc(security=None, responses={200: 'Success',
                                       400: 'Bad Request'
                                       })
    @api.marshal_list_with(a_package_details, envelope='packages')
    def get(self):
        packages = (Package.query.filter(Package.isArchived.is_(False))
                    .filter(Package.isExpired.is_(False))
                    .filter(Package.isApproved.is_(True)).all())
        view_packages = []
        for package in packages:
            ticket = Ticket.query.get(package.flight)
            hotel = Hotel.query.get(package.hotel)
            view_packages.append(
                {
                    'id': package.id,
                    'name': package.destination,
                    'details': {
                        'days': package.days,
                        'itinerary': package.intenerary,
                        'inclusions': package.inclusions,
                        'notes': package.note,
                        'date': ticket.departureDate
                    },
                    'price': package.price,
                    'ticket': {
                        'id': ticket.id,
                        'flightNo': ticket.flightNo,
                        'origin': ticket.origin,
                        'destination': ticket.arrival
                    },
                    'hotel': {
                        'id': hotel.id,
                        'name': hotel.name,
                        'roomType': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'remainingSlots': package.remainingSlots,
                    'expirationDate': package.expirationDate,
                    'isExpired': package.isExpired
                }
            )
        return view_packages, 200

    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                           })
    @token_required
    @api.expect(a_create_package)
    def post(self):
        errors.clear()
        data = api.payload
        try:
            name = data['name']
            days = int(data['details']['days'])
            itinerary = data['details']['itinerary']
            inclusions = data['details']['inclusions']
            notes = data['details']['notes']
            price = float(data['price'])
            remaining_slots = int(data['remainingSlots'])
            ticket = int(data['ticket'])
            hotel = int(data['hotel'])
            expiration_date = parse(data['expirationDate'])
            if data:
                if (not name or
                        not days or
                        not itinerary or
                        not inclusions or
                        not notes or
                        not price or
                        not remaining_slots or
                        not ticket or
                        not hotel or
                        not expiration_date):
                    if not name:
                        errors.append('Name must not be null')
                    if not days:
                        errors.append('Days must not be null')
                    if not itinerary:
                        errors.append('Itinerary must not be null')
                    if not inclusions:
                        errors.append('Inclusions must not be null')
                    if not notes:
                        errors.append('Notes must not be null')
                    if not price:
                        errors.append('Price must not be null')
                    if not remaining_slots:
                        errors.append('Remaining Slots must not be null')
                    if not ticket:
                        errors.append('Ticket must not be null')
                    if not hotel:
                        errors.append('Hotel must not be null')
                    if not expiration_date:
                        errors.append('Expiration Date must not be null')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': errors}}, 400
                elif (expiration_date <= now or
                        price <= 0 or
                        remaining_slots <= 0):
                    if expiration_date <= now:
                        errors.append('Expiration date must be not be less is equal '
                                      'to today\'s date')
                    if price <= 0:
                        errors.append('Price must be greater than zero')
                    if remaining_slots <= 0:
                        errors.append('Remaining slots must be greater than zero')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': errors}}, 400
                else:
                    new_package = Package(destination=name,
                                          price=price,
                                          days=days,
                                          intenerary=itinerary,
                                          inclusions=inclusions,
                                          remainingSlots=remaining_slots,
                                          expirationDate=expiration_date,
                                          note=notes,
                                          hotel=hotel,
                                          flight=ticket)
                    db.session.add(new_package)
                    db.session.commit()
                    return {'message': 'Successfully added new Packaged'}, 201
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400
        
    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Package Id', 'query')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, 
                            help='Id must not be null', location='args')
        args = parser.parse_args()
        id = args['id']
        errors.clear()
        if id:
            if id.isdigit():
                package = Package.query.get(id)
                if package:
                    package.isArchived = True
                    db.session.commit()
                    return {'message': 'Successfully archived'}, 200
                else:
                    errors.append('Package does no exist')
                    return {'errors': {'status': 400,
                                    'errorCode': 'E00P2',
                                    'message': errors}}, 400
            else:
                errors.append('Package Id must be an integer')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00P2',
                                   'message': errors}}, 400
        else:
            errors.append('Missing required parameter in the query string')
            return {'errors': {'status': 400,
                               'errorCode': 'E00P0',
                               'message': errors}}, 400
    
    @api.doc(security='apiKey', response={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Package Id', 'query')
    @api.expect(a_create_package)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()
        errors.clear()
        data = api.payload
        id = args['id']
        try:
            if id:
                if id.isdigit():
                    name = data['name']
                    days = int(data['details']['data'])
                    itinerary = data['details']['itinerary']
                    inclusions = data['details']['inclusions']
                    notes = data['details']['notes']
                    price = float(data['price'])
                    remaining_slots = int(data['remainingSlots'])
                    ticket = int(data['ticket'])
                    hotel = int(data['hotel'])
                    expiration_date = parse(data['expirationDate'])
                    if data:
                        if (not name or
                                not days or
                                not itinerary or
                                not inclusions or
                                not notes or
                                not price or
                                not remaining_slots or
                                not ticket or
                                not hotel or
                                not expiration_date):
                            if not name:
                                errors.append('Name must not be null')
                            if not days:
                                errors.append('Days must not be null')
                            if not itinerary:
                                errors.append('Itinerary must not be null')
                            if not inclusions:
                                errors.append('Inclusions must not be null')
                            if not notes:
                                errors.append('Notes must not be null')
                            if not price:
                                errors.append('Price must not be null')
                            if not remaining_slots:
                                errors.append('Remaining Slots must not be null')
                            if not ticket:
                                errors.append('Ticket must not be null')
                            if not hotel:
                                errors.append('Hotel must not be null')
                            if not expiration_date:
                                errors.append('Expiration Date must not be null')
                            return {'errors': {'status': 400,
                                            'errorCode': 'E0002',
                                            'message': errors}}, 400
                        elif (expiration_date >= now or
                                price <= 0 or
                                remaining_slots <= 0):
                            if expiration_date >= now:
                                errors.append('Expiration date must be not be less ir equal '
                                            'to today\'s date')
                            if price <= 0:
                                errors.append('Price must be greater than zero')
                            if remaining_slots <= 0:
                                errors.append('Remaining slots must be greater than zero')
                            return {'errors': {'status': 400,
                                            'errorCode': 'E0002',
                                            'message': errors}}, 400
                        else:
                            package = Package.query.get(id)
                            if not package:
                                errors.append('Package does not exist')
                                return {'errors': {'status': 400,
                                                   'errorCode': 'E2002',
                                                   'message': errors}}, 400
                            else:
                                package.destination=name
                                package.price=price
                                package.days=days
                                package.intenerary=itinerary
                                package.inclusions=inclusions
                                package.remainingSlots=remaining_slots
                                package.expirationDate=expiration_date
                                package.note=notes
                                package.hotel=hotel
                                package.flight=ticket
                                db.session.commit()
                                return {'message': 'Successfully updated Packaged'}, 200
                else:
                    errors.append('Package Id must be an integer')
                    return {'errors': {'status': 400,
                                    'errorCode': 'E00P2',
                                    'message': errors}}, 400
            else:
                errors.append('Missing required parameter in the query string')
                return {'errors': {'status': 400,
                                'errorCode': 'E00P0',
                                'message': errors}}, 400
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('/approval')
@api.response(404, 'Not Found')
class PackageApprovalApi(Resource):
    """Resource Class for Package Approval APIs"""

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Package Id', 'query')
    @api.expect(a_approve_package)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True, 
                            help='Id must not be null', location='args')
        args = parser.parse_args()
        data = api.payload
        id = args['id']
        errors.clear()
        try:
            if id:
                if id.isdigit():
                    package = Package.query.get(id)
                    if package:
                        approve = data['isApproved']
                        package.isApproved = approve
                        db.session.commit()
                        if approve:
                            return {'message': "Successfully Approved"}, 200
                        else:
                            return {'message': "Package not Approved"}, 200
                    else:
                        errors.append('Package not existing')
                        return {'errors': {'status': 400,
                                           'errorCode': 'E2002',
                                           'message': errors}}, 400
                else:
                    errors.append('Parameter in the query string must be an integer')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E00P0',
                                       'message': errors}}, 400
            else:
                errors.append('Missing required parameter in the query string')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00P0',
                                   'message': errors}}, 400
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400
    
    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @api.marshal_list_with(a_package_details, envelope='packages')
    def get(self):
        packages = (Package.query.filter(Package.isArchived.is_(False))
                    .filter(Package.isExpired.is_(False))
                    .filter(Package.isApproved.is_(False)).all())
        view_packages = []
        for package in packages:
            ticket = Ticket.query.get(package.flight)
            hotel = Hotel.query.get(package.hotel)
            view_packages.append(
                {
                    'id': package.id,
                    'name': package.destination,
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
                        'destination': ticket.arrival
                    },
                    'hotel': {
                        'id': hotel.id,
                        'name': hotel.name,
                        'roomType': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'remainingSlots': package.remainingSlots,
                    'expirationDate': package.expirationDate,
                    'isExpired': package.isExpired
                }
            )
        return view_packages, 200

@api.route('/hotels')
@api.response(404, 'Not Found')
class PackageApprovalHotelApi(Resource):
    """Resource class for Package Approval Hotel APIs"""

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_hotel_details, envelope="hotels")
    def get(self):
        hotels = (Hotel.query.filter(Hotel.isPackaged.is_(True))
                 .filter(Hotel.isArchived.is_(False))
                 .filter(Hotel.isExpired.is_(False)))
        view_hotels = []
        for hotel in hotels:
            view_hotels.append(
                {
                    'id': hotel.id,
                    'name': hotel.name,
                    'roomType': hotel.roomType,
                    'capacity': hotel.capacity
                })
        return view_hotels, 200

@api.route('/tickets')
@api.response(404, 'Not Found')
class PackageApprovalTicketApi(Resource):
    """Resource class for Package Approval Hotel APIs"""

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_ticket_details, envelope="flights")
    def get(self):
        tickets = (Ticket.query.filter(Ticket.isPackaged.is_(True))
                  .filter(Ticket.isArchived.is_(False))
                  .filter(Ticket.isExpired.is_(False)))
        view_tickets = []
        for ticket in tickets:
            view_tickets.append(
                {
                    'id': ticket.id,
                    'flightNo': ticket.flightNo,
                    'origin': ticket.origin,
                    'destination': ticket.arrival
                }
            )
        return view_tickets, 200