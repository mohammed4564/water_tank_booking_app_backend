from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import DriverSubscription, Driver, User
from helper.db import db
from datetime import datetime

driver_sub_bp = Blueprint('driver_sub_bp', __name__)

#Add a Driver Subscription (Admin / Platform Owner)
@driver_sub_bp.route('/add', methods=['POST'])
@jwt_required()
def add_driver_subscription():
    try:
        data = request.json
        driver_id = data.get('driver_id')
        amount = data.get('amount')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not driver_id or not amount or not start_date or not end_date:
            return jsonify({"error": "driver_id, amount, start_date, end_date are required"}), 400

        # Check driver exists
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        subscription = DriverSubscription(
            DriverId=driver_id,
            Amount=amount,
            StartDate=datetime.fromisoformat(start_date),
            EndDate=datetime.fromisoformat(end_date),
            Status='active',
            CreatedAt=datetime.utcnow()
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({"message": "Subscription added", "subscription_id": subscription.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#List All Subscriptions
@driver_sub_bp.route('/all', methods=['GET'])
@jwt_required()
def list_subscriptions():
    try:
        subscriptions = DriverSubscription.query.all()
        result = []
        for sub in subscriptions:
            result.append({
                "id": sub.Id,
                "driver_id": sub.DriverId,
                "driver_name": User.query.get(Driver.query.get(sub.DriverId).UserId).Name,
                "amount": sub.Amount,
                "start_date": sub.StartDate,
                "end_date": sub.EndDate,
                "status": sub.Status,
                "created_at": sub.CreatedAt,
                "updated_at": sub.UpdatedAt
            })
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Check Driver Subscription Status api
@driver_sub_bp.route('/status/<int:driver_id>', methods=['GET'])
@jwt_required()
def check_driver_subscription(driver_id):
    try:
        subscription = DriverSubscription.query.filter(
            DriverSubscription.DriverId==driver_id,
            DriverSubscription.Status=='active'
        ).order_by(DriverSubscription.EndDate.desc()).first()

        if not subscription:
            return jsonify({"status": "inactive"})

        return jsonify({
            "status": subscription.Status,
            "start_date": subscription.StartDate,
            "end_date": subscription.EndDate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500