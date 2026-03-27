from flask import Flask
from flask_cors import CORS
from helper.jwt_handler import init_jwt
from helper.db import init_db
from routes.user import user_bp
from routes.address import address_bp
from routes.driver import driver_bp
from routes.tanker import tanker_bp
from routes.booking import booking_bp
from routes.contact import contact_bp
from routes.notification import notification_bp
from routes.review import review_bp
from routes.driver_location import driver_location_bp
from routes.payment import payment_bp
from routes.water_price import water_price_bp
from routes.bill import bill_bp
from routes.driver_subscription import driver_sub_bp
from routes.subscription_payment import driver_payment_bp
from routes.water_source_subscription import water_source_sub_bp
from routes.subscription_plan import plan_bp
from routes.admin import admin_bp



app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# 🔌 Initialize DB
init_db(app)

# 🔐 Initialize JWT
init_jwt(app)

# 🔗 Register Routes
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(address_bp,url_prefix='/api/address')
app.register_blueprint(driver_bp, url_prefix='/api/driver')
app.register_blueprint(tanker_bp, url_prefix='/api/tanker')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(contact_bp, url_prefix='/api/contact')
app.register_blueprint(notification_bp, url_prefix='/api/notification')
app.register_blueprint(review_bp, url_prefix='/api/review')
app.register_blueprint(driver_location_bp, url_prefix='/api/driver-location')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(water_price_bp, url_prefix='/api/water-price')
app.register_blueprint(bill_bp, url_prefix='/api/bill')
app.register_blueprint(plan_bp, url_prefix='/api/plans')
app.register_blueprint(driver_sub_bp, url_prefix='/api/driver-subscription')
app.register_blueprint(driver_payment_bp, url_prefix='/api/subscription-payment')
app.register_blueprint(water_source_sub_bp, url_prefix='/api/water-source-subscription')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)