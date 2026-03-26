from flask import Blueprint, request, jsonify
from models import Booking, Tanker, Address
from helper.db import db
from flask_jwt_extended import jwt_required
from helper.jwt_handler import get_current_user_id
from datetime import datetime

booking_bp = Blueprint('booking_bp', __name__)

# Create Booking api 

@booking_bp.route('/create-booking', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        user_id = get_current_user_id()
        data = request.json

        tanker_id = data.get('tanker_id')
        address_id = data.get('address_id')
        total_price = data.get('total_price')
        scheduled_time = data.get('scheduled_time')
        payment_method = data.get('payment_method')

        if not tanker_id or not address_id or not total_price:
            return jsonify({"error": "Missing required fields"}), 400

        booking = Booking(
            UserId=user_id,
            TankerId=tanker_id,
            AddressId=address_id,
            TotalPrice=total_price,
            Status="pending",
            PaymentStatus="pending",
            PaymentMethod=payment_method,
            ScheduledTime=datetime.fromisoformat(scheduled_time) if scheduled_time else None,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(booking)
        db.session.commit()

        return jsonify({"message": "Booking created", "booking_id": booking.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Get My Bookings (User) api 
@booking_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def my_bookings():
    try:
        user_id = get_current_user_id()
        bookings = Booking.query.filter_by(UserId=user_id).all()

        result = []
        for b in bookings:
            result.append({
                "id": b.Id,
                "tanker_id": b.TankerId,
                "address_id": b.AddressId,
                "status": b.Status,
                "scheduled_time": b.ScheduledTime,
                "delivered_time": b.DeliveredTime,
                "total_price": b.TotalPrice,
                "payment_status": b.PaymentStatus,
                "payment_method": b.PaymentMethod
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Single Booking api

@booking_bp.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({
        "id": booking.Id,
        "user_id": booking.UserId,
        "tanker_id": booking.TankerId,
        "address_id": booking.AddressId,
        "status": booking.Status,
        "scheduled_time": booking.ScheduledTime,
        "delivered_time": booking.DeliveredTime,
        "total_price": booking.TotalPrice,
        "payment_status": booking.PaymentStatus,
        "payment_method": booking.PaymentMethod
    })

# Update Booking
@booking_bp.route('/update-booking/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        data = request.json
        booking.Status = data.get('status', booking.Status)
        booking.DeliveredTime = datetime.fromisoformat(data.get('delivered_time')) if data.get('delivered_time') else booking.DeliveredTime
        booking.TotalPrice = data.get('total_price', booking.TotalPrice)
        booking.PaymentStatus = data.get('payment_status', booking.PaymentStatus)
        booking.PaymentMethod = data.get('payment_method', booking.PaymentMethod)

        db.session.commit()
        return jsonify({"message": "Booking updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Delete Booking api
@booking_bp.route('/delete-booking/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
