from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Booking, Payment, User, Driver, Tanker, Address, WaterPrice, Bill
from helper.db import db
import json
from datetime import datetime

bill_bp = Blueprint('bill_bp', __name__)

# generate bill api 
@bill_bp.route('/generate/<int:booking_id>', methods=['POST'])
@jwt_required()
def generate_and_save_bill(booking_id):
    try:
        user_id = get_jwt_identity()

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        if booking.UserId != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        payment = Payment.query.filter_by(BookingId=booking.Id).first()
        if not payment:
            return jsonify({"error": "Payment not found for this booking"}), 404

        address = Address.query.get(booking.AddressId)
        tanker = Tanker.query.get(booking.TankerId)
        driver = Driver.query.get(tanker.DriverId)
        water_price = WaterPrice.query.filter_by(
            VehicleType=tanker.__class__.__name__,
            CapacityLiters=tanker.CapacityLiters,
            WaterType=tanker.WaterType
        ).first()

        bill_json = {
            "booking_id": booking.Id,
            "user": {
                "name": User.query.get(user_id).Name,
                "email": User.query.get(user_id).Email,
            },
            "driver": {
                "name": User.query.get(driver.UserId).Name,
                "license_number": driver.LicenseNumber,
                "vehicle_number": driver.VehicleNumber
            },
            "tanker": {
                "capacity_liters": tanker.CapacityLiters,
                "water_type": tanker.WaterType,
                "price_per_trip": water_price.PricePerTrip if water_price else tanker.PricePerTrip
            },
            "total_price": booking.TotalPrice,
            "payment": {
                "amount": payment.Amount,
                "payment_method": payment.PaymentMethod,
                "transaction_id": payment.TransactionId,
                "status": payment.Status,
                "paid_on": payment.CreatedAt
            },
            "delivery_address": {
                "address_line": address.AddressLine,
                "city": address.City,
                "state": address.State,
                "pincode": address.Pincode
            },
            "scheduled_time": booking.ScheduledTime,
            "delivered_time": booking.DeliveredTime
        }

        # Save bill in database
        bill = Bill(
            BookingId=booking.Id,
            PaymentId=payment.Id,
            BillData=json.dumps(bill_json),
            CreatedAt=datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()

        return jsonify({"message": "Bill generated and saved", "bill_id": bill.Id, "bill": bill_json})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Saved Bill API
@bill_bp.route('/<int:bill_id>', methods=['GET'])
@jwt_required()
def get_saved_bill(bill_id):
    try:
        bill = Bill.query.get(bill_id)
        if not bill:
            return jsonify({"error": "Bill not found"}), 404

        return jsonify({
            "bill_id": bill.Id,
            "booking_id": bill.BookingId,
            "payment_id": bill.PaymentId,
            "bill_data": json.loads(bill.BillData),
            "created_at": bill.CreatedAt,
            "updated_at": bill.UpdatedAt
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500