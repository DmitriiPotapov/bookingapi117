from flask_restplus import Namespace, fields

api = Namespace('Tickets', 'Ticket Related APIs', path='/tickets')

a_ticket_basics_details = api.model('Basic Details',
                                    {'location': fields.String(),
                                     'date': fields.Date(),
                                     'time': fields.String()
                                    })

a_ticket_timestamp = api.model('Timestamp',
                               {'dateCreated': fields.DateTime(),
                                'dateUpdated': fields.DateTime()
                               })

a_ticket_details = api.model('Ticket Details',
                             {'id': fields.Integer(),
                              'flightNo': fields.String(),
                              'origin': fields.Nested(a_ticket_basics_details),
                              'return': fields.Nested(a_ticket_basics_details),
                              'remainingSlots': fields.Integer(),
                              'price': fields.Float(),
                              'expirationDate': fields.Date(),
                              'isExpired': fields.Boolean(),
                              'isPackaged': fields.Boolean(),
                              'timestamp': fields.Nested(a_ticket_timestamp)
                             })
                             
a_create_ticket = api.model('Create Ticket',
                            {'flightNo': fields.String(),
                             'origin': fields.Nested(a_ticket_basics_details),
                             'return': fields.Nested(a_ticket_basics_details),
                             'remainingSlots': fields.Integer(),
                             'price': fields.Float(),
                             'expirationDate': fields.Date(),
                             'isPackaged': fields.Boolean()
                            })

a_approve_ticket = api.model('Approve Ticket',
                             {'isApproved': fields.Boolean()})
