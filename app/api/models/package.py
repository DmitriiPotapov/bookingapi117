from flask_restplus import Namespace, fields

api = Namespace('Packages', 'Package related APIs', path='/packages')

a_timestamp = api.model('Timestamp',
                        {'dateCreated': fields.DateTime(),
                         'dateUpdated': fields.DateTime()
                         })

a_ticket_details = api.model('Ticket Package Details', 
                            {'id': fields.Integer(),
                             'flightNo': fields.String(),
                             'origin': fields.String(),
                             'destination': fields.String()
                             })

a_hotel_details = api.model('Hotel Pakage Details',
                           {'id': fields.Integer(),
                            'name': fields.String(),
                            'roomType': fields.String(),
                            'capacity': fields.Integer()
                            })

a_package_specification = api.model('Package Specifications',
                                   {'days': fields.String(),
                                    'itinerary': fields.String(),
                                    'inclusions': fields.String(),
                                    'notes': fields.String(),
                                    'date': fields.Date()
                                    })

a_package_details = api.model('Package Details',
                              {'id': fields.Integer(),
                              'name': fields.String(),
                              'departureDate': fields.Date(),
                              'details': fields.Nested(a_package_specification),
                              'price': fields.Float(),
                              'ticket': fields.Nested(a_ticket_details),
                              'hotel': fields.Nested(a_hotel_details),
                              'remainingSlots': fields.Integer(),
                              'expirationDate': fields.Date(),
                              'isExpired': fields.Boolean()
                              })

a_create_package = api.model('Create Package',
                             {'name': fields.String(),
                              'details': fields.Nested(a_package_specification),
                              'price': fields.Float(),
                              'ticket': fields.Integer(),
                              'hotel': fields.Integer(),
                              'remainingSlots': fields.Integer(),
                              'expirationDate': fields.Date()
                              })

a_approve_package = api.model('Approve Package',
                              {'isApproved': fields.Boolean()})

a_archive_package = api.model('Archive Package',
                              {'isArchived': fields.Boolean()})
