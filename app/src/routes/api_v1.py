from flask import Blueprint
from flask_restplus import Api
from app.src.helpers.decorators import authentication
from app.api.controller.user import api as user_api
from app.api.controller.ticket import api as ticket_api
from app.api.controller.hotel import api as hotel_api
from app.api.controller.package import api as package_api
from app.api.controller.booking import api as booking_api
from app.api.controller.payment import api as payment_api
from app.api.controller.inquiry import api as inquiry_api

api_routes = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_routes, title='First Choice Travel Hub API', 
          version='1', doc='/documentation', authorizations=authentication)

api.add_namespace(user_api)
api.add_namespace(ticket_api)
api.add_namespace(hotel_api)
api.add_namespace(package_api)
api.add_namespace(payment_api)
api.add_namespace(booking_api)
api.add_namespace(inquiry_api)
