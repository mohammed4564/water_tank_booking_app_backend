from flask import Blueprint, request, jsonify
from helper.db import db
from models import SubscriptionPayment, DriverSubscription
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
driver_payment_bp = Blueprint('driver_payment_bp', __name__)

#Add Payment API

@driver_payment_bp.route('/add-payment', methods=['POST'])
@jwt_required()
def add_payment():
    try:
        data = request.json

        subscription_id = data.get('subscription_id')
        payment_method = data.get('payment_method')

        if not subscription_id or not payment_method:
            return jsonify({"error": "Missing required fields"}), 400

        subscription = DriverSubscription.query.get(subscription_id)
        if not subscription:
            return jsonify({"error": "Subscription not found"}), 404

        # ❌ Prevent double payment
        existing_payment = SubscriptionPayment.query.filter_by(
            SubscriptionId=subscription_id,
            PaymentStatus='Paid'
        ).first()

        if existing_payment:
            return jsonify({"error": "Subscription already paid"}), 400

        # ❌ Prevent paying active subscription again
        if subscription.Status == 'Active':
            return jsonify({"error": "Subscription already active"}), 400

        # ❌ Prevent paying expired subscription
        if subscription.EndDate < datetime.utcnow():
            return jsonify({"error": "Subscription expired. Create new subscription"}), 400

        # ✅ Create payment (Pending verification)
        payment = SubscriptionPayment(
            SubscriptionId=subscription_id,
            Amount=subscription.Amount,
            PaymentMethod=payment_method,
            PaymentStatus='Paid',
            VerifyStatus='Pending',  # 🔥 important
            TransactionId=data.get('transaction_id'),
            PaidAt=datetime.utcnow()
        )

        # ❌ DO NOT ACTIVATE HERE
        # subscription.Status = 'Active'  ← REMOVE THIS

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "message": "Payment submitted. Waiting for admin verification.",
            "payment_id": payment.Id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
#Get All Payments
@driver_payment_bp.route('/payments', methods=['GET'])
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
@driver_payment_bp.route('/payments/<int:subscription_id>', methods=['GET'])
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
@driver_payment_bp.route('/update-payment/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    try:
        payment = SubscriptionPayment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        data = request.json
        status = data.get('payment_status')

        if status:
            payment.PaymentStatus = status

            # 🔥 Sync subscription
            if status == 'Paid':
                payment.PaidAt = datetime.utcnow()
                payment.subscription.Status = 'Active'

            elif status == 'Failed':
                payment.subscription.Status = 'Pending'

        db.session.commit()

        return jsonify({"message": "Payment updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Delete Payment
@driver_payment_bp.route('/delete-payment/<int:payment_id>', methods=['DELETE'])
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