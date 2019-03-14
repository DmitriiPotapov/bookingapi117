from flask_restplus import Namespace, fields

api = Namespace('Bookings', 'Booking Related APIs', path='/bookings')

a_name = api.model('Name',
                   {'first': fields.String(),
                    'middle': fields.String(),
                    'last': fields.String()
                    })

a_user_details = api.model('Customer Details',
                           {'id': fields.Integer(),
                            'name': fields.Nested(a_name),
                            'email': fields.String()
                            })

a_ticket_basics_details = api.model('Ticket Basic Details',
                                    {'location': fields.String(),
                                     'date': fields.Date(),
                                     'time': fields.String()
                                     })

a_ticket_details = api.model('Ticket Details',
                             {'id': fields.Integer(),
                              'flightNo': fields.String(),
                              'origin': fields.Nested(a_ticket_basics_details),
                              'return': fields.Nested(a_ticket_basics_details),
                              'remainingSlots': fields.Integer(),
                              'price': fields.Float(),
                              'expirationDate': fields.Date()
                              })

a_ticket_booking_details = api.model('Ticket Booking Details',
                                     {'id': fields.Integer(),
                                      'referenceNumber': fields.String(),
                                    #   'customer': fields.Nested(a_user_details),
                                      'ticket': fields.Nested(a_ticket_details),
                                      'isPaid': fields.Boolean(),
                                      'status': fields.String()
                                      })

a_ticket_booking = api.model('Ticket Booking',
                            {'ticket': fields.Integer()})

a_hotel_room = api.model('Room Details', 
                         {'type': fields.String(),
                          'capacity': fields.String()
                         })

a_hotel_check_date = api.model('Check Dates', 
                               {'in': fields.Date(), 
                                'out': fields.Date()
                               })

a_hotel_details = api.model('Hotel Details', 
                            {'id': fields.Integer(),
                             'name': fields.String(),
                             'room': fields.Nested(a_hotel_room),
                             'details': fields.String(),
                             'checkDates': fields.Nested(a_hotel_check_date),
                             'price': fields.Float(),
                             'expirationDate': fields.Date(),
                             'remainingRooms': fields.Integer(),
                            })

a_hotel_booking_details = api.model('Hotel Booking Details',
                                    {'id': fields.Integer(),
                                     'referenceNumber': fields.String(),
                                     'customer': fields.Nested(a_user_details),
                                     'hotel': fields.Nested(a_hotel_details),
                                     'isPaid': fields.Boolean(),
                                     'status': fields.String()
                                     })

a_hotel_booking = api.model('Hotel Booking',
                            {'hotel': fields.Integer()})

a_ticket_details_package = api.model('Ticket Package Details', 
                            {'id': fields.Integer(),
                             'flightNo': fields.String(),
                             'origin': fields.String(),
                             'destination': fields.String()
                             })

a_hotel_details_package = api.model('Hotel Pakage Details',
                           {'id': fields.Integer(),
                            'name': fields.String(),
                            'roomType': fields.String(),
                            'capacity': fields.Integer()
                            })

a_package_specification = api.model('Package Specifications',
                                   {'days': fields.String(),
                                    'itinerary': fields.String(),
                                    'inclusions': fields.String(),
                                    'notes': fields.String()
                                    })

a_package_details = api.model('Package Details',
                              {'id': fields.Integer(),
                              'name': fields.String(),
                              'details': fields.Nested(a_package_specification),
                              'price': fields.Float(),
                              'ticket': fields.Nested(a_ticket_details_package),
                              'hotel': fields.Nested(a_hotel_details_package),
                              'remainingSlots': fields.Integer(),
                              'expirationDate': fields.Date(),
                              })

a_package_booking_details = api.model('Package Booking Detials',
                                      {'id': fields.Integer(),
                                       'referenceNumber': fields.Integer(),
                                       'customer': fields.Nested(a_user_details),
                                       'package': fields.Nested(a_package_details),
                                       'isPaid': fields.Boolean(),
                                       'status': fields.String()})

a_package_booking = api.model('Package Booking',
                              {'package': fields.Integer()})
