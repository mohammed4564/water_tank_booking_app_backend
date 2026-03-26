from flask import Blueprint, request, jsonify
from models import Payment
from helper.db import db
from flask_jwt_extended import jwt_required
from datetime import datetime

payment_bp = Blueprint('payment_bp', __name__)

#Add Payment API 
@payment_bp.route('/add-payment', methods=['POST'])
@jwt_required()
def add_payment():
    try:
        data = request.json
        booking_id = data.get('booking_id')
        amount = data.get('amount')
        method = data.get('payment_method')
        transaction_id = data.get('transaction_id')
        status = data.get('status', 'pending')

        if not booking_id or amount is None:
            return jsonify({"error": "booking_id and amount are required"}), 400

        payment = Payment(
            BookingId=booking_id,
            Amount=amount,
            PaymentMethod=method,
            TransactionId=transaction_id,
            Status=status,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({"message": "Payment recorded successfully", "payment_id": payment.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Payments by Booking
@payment_bp.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking_payments(booking_id):
    try:
        payments = Payment.query.filter_by(BookingId=booking_id).all()
        result = []
        for p in payments:
            result.append({
                "id": p.Id,
                "booking_id": p.BookingId,
                "amount": p.Amount,
                "payment_method": p.PaymentMethod,
                "transaction_id": p.TransactionId,
                "status": p.Status,
                "created_at": p.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Get All Payments (Admin)
@payment_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_payments():
    try:
        payments = Payment.query.all()
        result = []
        for p in payments:
            result.append({
                "id": p.Id,
                "booking_id": p.BookingId,
                "amount": p.Amount,
                "payment_method": p.PaymentMethod,
                "transaction_id": p.TransactionId,
                "status": p.Status,
                "created_at": p.CreatedAt
            })
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
