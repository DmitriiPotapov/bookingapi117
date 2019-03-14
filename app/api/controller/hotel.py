from flask_restplus import Resource, reqparse
from app.src.models import db, Hotel
from app.api.models.hotel import api, a_create_hotel, a_hotel_details, a_approve_hotel
from app.src.helpers.decorators import token_required
from datetime import datetime, timedelta
from dateutil.parser import parse

errors = []
now = datetime.now()

@api.route('')
@api.response(404, 'Not Found')
class HotelApi(Resource):
    """Resource Class for Hotel APIs

    Hotel API for endpoint api/v1/hotels with methods GET, POST, DELETE, AND PUT
    """

    @api.doc(security=None, responses={200: 'Success', 400: 'Bad Request'})
    @api.marshal_list_with(a_hotel_details, envelope='hotels')
    def get(self):
        """GET method for endpoint api/v1/hotels
        
        :returns: a list of dictionaries containing hotel details

        :rtype: list
        """

        hotels = (Hotel.query.filter(Hotel.isArchived.is_(False))
                  .filter(Hotel.isExpired.is_(False))
                  .filter(Hotel.isPackaged.is_(False))
                  .filter(Hotel.isApproved.is_(True)).all())
        view_hotels = []
        for hotel in hotels:
            view_hotels.append(
                {
                    'id': hotel.id,
                    'name': hotel.name,
                    'room': {
                        'type': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'details': hotel.details,
                    'checkDates': {
                        'in': hotel.checkIn,
                        'out': hotel.checkOut
                    },
                    'price': hotel.price,
                    'expirationDate': hotel.expirationDate,
                    'isExpired': hotel.isExpired,
                    'isPackaged': hotel.isPackaged,
                    'remainingRooms': hotel.remainingRooms,
                    'timestamp': {
                        'dateCreated': hotel.dateCreated,
                        'dateUpdated': hotel.dateUpdated
                    }
                }
            )
        return view_hotels, 200

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.expect(a_create_hotel)
    def post(self):
        """POST method for endpoint api/v1/hotels

        :returns : a dictionary listing either an error or success

        :rtype : dict
        """

        errors.clear()
        data = api.payload
        try:
            name = data['name']
            room_details = data['room']['type']
            capacity = int(data['room']['capacity'])
            details = data['details']
            check_in = parse(data['checkDates']['in'])
            check_out = parse(data['checkDates']['out'])
            price = float(data['price'])
            expiration_date = parse(data['expirationDate'])
            is_packaged = data['isPackaged']
            remaining_rooms = int(data['remainingRooms'])
            if (not name or
                    not room_details or
                    not capacity or
                    not details or
                    not check_in or
                    not check_out or
                    not price or
                    not expiration_date or
                    not remaining_rooms):
                if not name:
                    errors.append('Hotel Name must not be null')
                elif not room_details:
                    errors.append('Room Details must not be null')
                elif not capacity:
                    errors.append('Capacity must not be null')
                elif not check_in:
                    errors.append('Check in date must not be null')
                elif not check_out:
                    errors.append('Check out date must not be null')
                elif not price:
                    errors.append('Price must not be null')
                elif not expiration_date:
                    errors.append('Expiration Date must not be null')
                elif not remaining_rooms:
                    errors.append('Remaining Rooms must not be null')
                return {'errors': {'status': 400,
                                   'errorsCodes': 'E00H2',
                                   'message': errors}}, 400
            elif (check_in <= now or
                    check_out <= now or
                    expiration_date <= now or
                    expiration_date >= check_in or
                    price <= 0 or
                    remaining_rooms <= 0):
                if check_in <= now:
                    errors.append('Check in date must not be greater than '
                                  'or equal to today\'s date')
                elif check_out <= now:
                    errors.append('Check out date must not be greater than '
                                  'or equal to today\'s date')
                elif expiration_date <= now:
                    errors.append('Expiration Date must not be greater than '
                                  'or equal to today\'s date')
                elif expiration_date >= check_in:
                    errors.append('Expiration Date must not be greater than '
                                  'or equal to check in date')
                elif price <= 0:
                    errors.append('Price must be greater than zero')
                return {'errors': {'status': 400,
                                   'errorCodes': 'E00H2',
                                   'message': errors}}, 400
            else:
                new_hotel = Hotel(name=name,
                                  roomType=room_details,
                                  capacity=capacity,
                                  details=details,
                                  checkIn=check_in,
                                  checkOut=check_out,
                                  price=price,
                                  expirationDate=expiration_date,
                                  remainingRooms=remaining_rooms,
                                  isPackaged=is_packaged)
                db.session.add(new_hotel)
                db.session.commit()
                return {'message': 'Successfully added new hotel'}, 201
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

    @api.doc(security="apiKey", responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Hotel Id', 'query')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True,
                            help='Id must not be null', location='args')
        args =  parser.parse_args()
        id = args['id']
        errors.clear()
        if id:
            if id.isdigit():
                hotel = Hotel.query.get(id)
                if hotel:
                    hotel.isArchived = True
                    db.session.commit()
                    return {'message': 'Successfully archived'}, 200
                else:
                    errors.append('Hotel does no exist')
                    return {'errors': {'status': 400,
                                    'errorCode': 'E00H2',
                                    'message': errors}}, 400
            else:
                errors.append('Hotel Id must be an integer')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00H2',
                                   'message': errors}}, 400
        else:
            errors.append('Missing required parameter in the query string')
            return {'errors': {'status': 400,
                               'errorCode': 'E00H0',
                               'message': errors}}, 400
    
    @api.doc(security="apiKey", responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Hotel Id', 'query')
    @api.expect(a_create_hotel)
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
                    room_details = data['room']['type']
                    capacity = int(data['room']['capacity'])
                    details = data['details']
                    check_in = parse(data['checkDates']['in'])
                    check_out = parse(data['checkDates']['out'])
                    price = float(data['price'])
                    expiration_date = parse(data['expirationDate'])
                    is_packaged = data['isPackaged']
                    remaining_rooms = int(data['remainingRooms'])
                    if data:
                        if (not name or
                                not room_details or
                                not capacity or
                                not details or
                                not check_in or
                                not check_out or
                                not price or
                                not expiration_date or
                                not remaining_rooms):
                            if not name:
                                errors.append('Hotel Name must not be null')
                            elif not room_details:
                                errors.append('Room Details must not be null')
                            elif not capacity:
                                errors.append('Capacity must not be null')
                            elif not check_in:
                                errors.append('Check in date must not be null')
                            elif not check_out:
                                errors.append('Check out date must not be null')
                            elif not price:
                                errors.append('Price must not be null')
                            elif not expiration_date:
                                errors.append('Expiration Date must not be null')
                            elif not remaining_rooms:
                                errors.append('Remaining Rooms must not be null')
                            return {'errors': {'status': 400,
                                            'errorsCodes': 'E00H2',
                                            'message': errors}}, 400
                        elif (check_in <= now or
                                check_out <= now or
                                expiration_date <= now or
                                expiration_date >= check_in or
                                price <= 0 or
                                remaining_rooms <= 0):
                            if check_in <= now:
                                errors.append('Check in date must not be greater than '
                                            'or equal to today\'s date')
                            elif check_out <= now:
                                errors.append('Check out date must not be greater than '
                                            'or equal to today\'s date')
                            elif expiration_date <= now:
                                errors.append('Expiration Date must not be greater than '
                                            'or equal to today\'s date')
                            elif expiration_date >= check_in:
                                errors.append('Expiration Date must not be greater than '
                                            'or equal to check in date')
                            elif price <= 0:
                                errors.append('Price must be greater than zero')
                            return {'errors': {'status': 400,
                                            'errorCodes': 'E00H2',
                                            'message': errors}}, 400
                        else:
                            hotel = Hotel.query.get(id)
                            if not hotel:
                                errors.append('Id not existing')
                                return {'errors': {'status': 400,
                                                   'errorCode': 'E2002',
                                                   'message': errors}}, 400
                            else:
                                hotel.name = name
                                hotel.roomType = room_details
                                hotel.capacity = capacity
                                hotel.details = details
                                hotel.checkIn = check_in
                                hotel.checkOut = check_out
                                hotel.price = price
                                hotel.expirationDate = expiration_date
                                hotel.remainingRooms = remaining_rooms
                                hotel.isPackaged = is_packaged
                                db.session.commit()
                                return {'message': 'Successfully updated hotel'}, 200
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
class HotelApprovalApi(Resource):
    """Resource  Class for Hotel Approval APIs

    """

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('id', 'Hotel Id', 'query')
    @api.expect(a_approve_hotel)
    def put(self):
        """PUT Method for endpoint api/v1/hotels/approval"""

        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()
        errors.clear()
        data = api.payload
        id = args['id']
        try:
            if id:
                if id.isdigit():
                    hotel = Hotel.query.get(id)
                    if hotel:
                        approve = data['isApproved']
                        hotel.isApproved = approve
                        db.session.commit()
                        if approve:
                            return {'message': "Successfully Approved"}, 200
                        else:
                            return {'message': "Ticket not Approved"}, 200
                    else:
                        errors.append('Id not existing')
                        return {'errors': {'status': 400,
                                           'errorCode': 'E2002',
                                           'message': errors}}, 400
                else:
                    errors.append('Parameter in the query string must be an integer')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E00H0',
                                       'message': errors}}, 400
            else:
                errors.append('Missing required parameter in the query string')
                return {'errors': {'status': 400,
                                   'errorCode': 'E00H0',
                                   'message': errors}}, 400
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

    @api.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_hotel_details, envelope='hotels')
    def get(self):
        """GET method for endpoint api/v1/hotels/approval
        
        :returns: a list of dictionaries containing hotel details for approval

        :rtype: list
        """

        hotels = (Hotel.query.filter(Hotel.isArchived.is_(False))
                  .filter(Hotel.isExpired.is_(False))
                  .filter(Hotel.isPackaged.is_(False))
                  .filter(Hotel.isApproved.is_(False)).all())
        view_hotels = []
        for hotel in hotels:
            view_hotels.append(
                {
                    'id': hotel.id,
                    'name': hotel.name,
                    'room': {
                        'type': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'details': hotel.details,
                    'checkDates': {
                        'in': hotel.checkIn,
                        'out': hotel.checkOut
                    },
                    'price': hotel.price,
                    'expirationDate': hotel.expirationDate,
                    'isExpired': hotel.isExpired,
                    'isPackaged': hotel.isPackaged,
                    'remainingRooms': hotel.remainingRooms,
                    'timestamp': {
                        'dateCreated': hotel.dateCreated,
                        'dateUpdated': hotel.dateUpdated
                    }
                }
            )
        return view_hotels, 200

@api.route('/id=<int:id>')
@api.response(404, 'Not Found')
class HotelIdApi(Resource):
    """Resource class for Hotel Id Apis"""

    @api.doc(security=None, responses={200: 'Success',
                                       400: 'Bad Request'})
    def get(self, id):
        """GET Method for api/v1/hotels/id=idParams 
        
        :returns : a dictionary listing the details of the hotel
        :rtype : dict
        """
        errors.clear()
        hotel = (Hotel.query.filter(Hotel.isArchived.is_(False))
                 .filter(Hotel.isExpired.is_(False))
                 .filter(Hotel.isPackaged.is_(False))
                 .filter(Hotel.id == id).first())
        if hotel:
            view_hotel = {
                            'id': hotel.id,
                            'name': hotel.name,
                            'room': {
                                'type': hotel.roomType,
                                'capacity': hotel.capacity
                            },
                            'details': hotel.details,
                            'checkDates': {
                                'in': hotel.checkIn,
                                'out': hotel.checkOut
                            },
                            'price': hotel.price,
                            'expirationDate': hotel.expirationDate,
                            'isExpired': hotel.isExpired,
                            'isPackaged': hotel.isPackaged,
                            'remainingRooms': hotel.remainingRooms,
                            'timestamp': {
                                'dateCreated': hotel.dateCreated,
                                'dateUpdated': hotel.dateUpdated
                            }
                        }
            return api.marshal(view_hotel, a_hotel_details,
                               envelope='hotel'), 200
        else:
            errors.append('Flight does not exist')
            return {'errors': {'status': 400,
                               'errorCode': 'E00H2',
                               'message': errors}}, 400