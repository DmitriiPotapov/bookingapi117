from flask_restplus import Namespace, fields

api = Namespace('Hotels', 'Hotel Related APIs', path='/hotels')

a_hotel_room = api.model('Room Details', 
                         {'type': fields.String(),
                          'capacity': fields.String()
                         })

a_hotel_check_date = api.model('Check Dates', 
                               {'in': fields.Date(), 
                                'out': fields.Date()
                               })

a_hotel_timestamp = api.model('Timestamp', 
                              {'dateCreated': fields.DateTime(),
                               'dateUpdated': fields.DateTime()
                              })

a_hotel_details = api.model('Hotel Details', 
                            {'id': fields.Integer(),
                             'name': fields.String(),
                             'room': fields.Nested(a_hotel_room),
                             'details': fields.String(),
                             'checkDates': fields.Nested(a_hotel_check_date),
                             'price': fields.Float(),
                             'expirationDate': fields.Date(),
                             'isExpired': fields.Boolean(),
                             'isPackaged': fields.Boolean(),
                             'remainingRooms': fields.Integer(),
                             'timestamp': fields.Nested(a_hotel_timestamp)
                            })

a_create_hotel = api.model('Create Hotel',
                           {'name': fields.String(),
                            'room': fields.Nested(a_hotel_room),
                            'details': fields.String(),
                            'checkDates': fields.Nested(a_hotel_check_date),
                            'price': fields.Float(),
                            'expirationDate': fields.Date(),
                            'isPackaged': fields.Boolean(),
                            'remainingRooms': fields.Integer(),
                           })

a_approve_hotel = api.model('Approve Hotel',
                            {'isApproved': fields.Boolean()})
