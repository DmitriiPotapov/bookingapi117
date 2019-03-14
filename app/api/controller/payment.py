import stripe
# from flask import request
from flask_restplus import Resource
from flask_mail import Message
from app.src.models import db, Payments, Hotel, Ticket, Package
from app.src.models import FlightBooking, HotelBooking, PackageBooking
from app.src.models import StripeCustomer
from app.api.models.payment import api, a_create_stripe_charges, a_stripe_details
from app.src.helpers.decorators import referenceNumber, token_required
from app.api.controller.user import mail
from flask import Flask, render_template, make_response
import pdfkit


errors = []

pubkey = 'pk_test_GjK3GmJJ1exs60wIcgTpfggq'
secretkey = 'sk_test_RXyvP1FBgkRyCwyEBGyZeymo'

stripe.api_key = secretkey

# def pdf_template(name, Location):
#     rendered = render_template('invoice_template.html', name = name, Location = location)
#     pdf = pdfkit.from_string(rendered, False)
    
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application.pdf'
#     response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

#     return response


def pdf_template():
    rendered = render_template('invoice_template.html')
    pdf = pdfkit.from_string(rendered, False)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application.pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

    return response


@api.route('')
@api.response(404, 'Not Found')
class PaymentApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.expect(a_create_stripe_charges)
    def post(self):
        errors.clear()
        data = api.payload
        try:
            booking = data['referenceNumber']
            email = data['email']
            token = data['token']
            amount = data['amount']
            description = data['description']
            payment_for = data['paymentFor']
            customer = (StripeCustomer.query
                    .filter(StripeCustomer.email == email).first())
            if customer is None:
                customer_stripe = (stripe.Customer.create(email=email,
                                                          source=token))
                new_customer = StripeCustomer(email=email,
                                              stripeCustomerId=customer_stripe.id)
                db.session.add(new_customer)
                db.session.flush()
                db.session.commit()
                customer = (StripeCustomer.query
                            .filter(StripeCustomer.email == email).first())
            charge = stripe.Charge.create(customer=customer.stripeCustomerId,
                                          amount=int(amount/100),
                                          currency='php',
                                          description=description)
            payment_reference = 'PC' + referenceNumber
            new_payment = Payments(paymentReference=payment_reference,
                                   bookingReference=booking,
                                   paymentFor=payment_for,
                                   stripeCustomer=customer.id,
                                   stripeChargeId=charge.id)
            db.session.add(new_payment)
            db.session.commit()
            if payment_for == 'Packages':
                package = PackageBooking.query.filter(PackageBooking.referenceNumber == booking)
                package.update({PackageBooking.isPaid: True})
                db.session.commit()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200
            if payment_for == 'Hotels':
                hotel = HotelBooking.query.filter(HotelBooking.referenceNumber == booking)
                hotel.update({HotelBooking.isPaid: True})
                db.session.commit()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200
            if payment_for == 'Tickets':
                ticket = FlightBooking.query.filter(FlightBooking.referenceNumber == booking)
                ticket.update({FlightBooking.isPaid: True})
                db.session.commit()
                
                invoice_template = pdf_template()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200


        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400
