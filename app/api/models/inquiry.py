from flask_restplus import Namespace, fields

api = Namespace('Inquiries', 'Inquiries Related APIs', path='/inquiries')

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

a_inquiries_flight_basic_details = api.model('Basic Details',
                                             {'location': fields.String(),
                                              'date': fields.Date()
                                             })

a_inquiries_flight = api.model('Flight Details',
                               {'origin': fields.Nested(a_inquiries_flight_basic_details),
                                'departure': fields.Nested(a_inquiries_flight_basic_details)})

a_inquiries_flight_passenger = api.model('Passenger Count',
                                         {'adult': fields.Integer(),
                                          'child': fields.Integer(),
                                          'infant': fields.Integer()
                                         })

a_inquiries_flight_details = api.model('Flight Inquiries',
                                       {'id': fields.Integer(),
                                        'customer': fields.Nested(a_user_details),
                                        'flight': fields.Nested(a_inquiries_flight),
                                        'time': fields.String(),
                                        'passenger': fields.Nested(a_inquiries_flight_passenger),
                                        'note': fields.String()
                                       })

a_inquiries_flight_create = api.model('Create Flight Inquiries',
                                      {'flight': fields.Nested(a_inquiries_flight),
                                       'passenger': fields.Nested(a_inquiries_flight_passenger),
                                       'note': fields.String()
                                      })

a_inquiries_delete_flight = api.model('Delete Flight Inquiry',
                                      {'isArchived': fields.Boolean()})

a_inquiries_hotel_dates = api.model('Check Dates',
                                    {'in': fields.Date(),
                                     'out': fields.Date()
                                    })

a_inquiries_hotel_room_details = api.model('Room Details',
                                           {'location': fields.String(),
                                            'budget': fields.String()
                                           })

a_inquiries_hotel_details = api.model('Create Hotel Inquiries',
                                      {'id':fields.Integer(),
                                       'customer': fields.Nested(a_user_details),
                                       'hotel': fields.Nested(a_inquiries_hotel_room_details),
                                       'checkDates': fields.Nested(a_inquiries_hotel_dates),
                                       'guestNumber': fields.Integer(),
                                       'note': fields.String()
                                      })

a_inquiries_hotel_create = api.model('Create Hotel Inquiries',
                                     {'hotel': fields.Nested(a_inquiries_hotel_room_details),
                                      'checkDates': fields.Nested(a_inquiries_hotel_dates),
                                      'guestNumber': fields.Integer(),
                                      'note': fields.String()
                                     })

a_inquiries_delete_hotel = api.model('Delete Flight Inquiry',
                                     {'isArchived': fields.Boolean()})
