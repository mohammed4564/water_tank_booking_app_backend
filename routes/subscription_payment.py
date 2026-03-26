from flask import Blueprint, request, jsonify
from helper.db import db
from models import SubscriptionPayment, DriverSubscription
from datetime import datetime
from flask_jwt_extended import jwt_required

payment_bp = Blueprint('payment_bp', __name__)

#Add Payment API

@payment_bp.route('/add-payment', methods=['POST'])
@jwt_required()
def add_payment():
    try:
        data = request.json

        if not data.get('subscription_id') or not data.get('amount') or not data.get('payment_method'):
            return jsonify({"error": "Missing required fields"}), 400

        # Check subscription exists
        subscription = DriverSubscription.query.get(data.get('subscription_id'))
        if not subscription:
            return jsonify({"error": "Subscription not found"}), 404

        payment = SubscriptionPayment(
            SubscriptionId=data.get('subscription_id'),
            Amount=data.get('amount'),
            PaymentMethod=data.get('payment_method'),
            PaymentStatus=data.get('payment_status', 'Pending'),
            TransactionId=data.get('transaction_id'),
            PaidAt=datetime.utcnow() if data.get('payment_status') == 'Paid' else None
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "message": "Payment added successfully",
            "payment_id": payment.Id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get All Payments
@payment_bp.route('/payments', methods=['GET'])
def get_payments():
    try:
        payments = SubscriptionPayment.query.all()
        result = []

        for p in payments:
            result.append({
                "id": p.Id,
                "subscription_id": p.SubscriptionId,
                "amount": float(p.Amount),
                "payment_method": p.PaymentMethod,
                "payment_status": p.PaymentStatus,
                "transaction_id": p.TransactionId,
                "paid_at": p.PaidAt,
                "created_at": p.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get Payments by Subscription
@payment_bp.route('/payments/<int:subscription_id>', methods=['GET'])
def get_payments_by_subscription(subscription_id):
    try:
        payments = SubscriptionPayment.query.filter_by(SubscriptionId=subscription_id).all()

        result = []
        for p in payments:
            result.append({
                "id": p.Id,
                "amount": float(p.Amount),
                "payment_method": p.PaymentMethod,
                "payment_status": p.PaymentStatus,
                "transaction_id": p.TransactionId,
                "paid_at": p.PaidAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Update Payment Status
@payment_bp.route('/update-payment/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    try:
        payment = SubscriptionPayment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        data = request.json

        payment.PaymentStatus = data.get('payment_status', payment.PaymentStatus)

        if data.get('payment_status') == 'Paid':
            payment.PaidAt = datetime.utcnow()

        db.session.commit()

        return jsonify({"message": "Payment updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Delete Payment
@payment_bp.route('/delete-payment/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    try:
        payment = SubscriptionPayment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        db.session.delete(payment)
        db.session.commit()

        return jsonify({"message": "Payment deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500