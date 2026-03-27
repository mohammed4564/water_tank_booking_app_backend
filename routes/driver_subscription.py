from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import DriverSubscription, Driver, User
from helper.db import db
from datetime import datetime,timedelta
from helper.jwt_handler import get_jwt_identity

driver_sub_bp = Blueprint('driver_sub_bp', __name__)

#Add a Driver Subscription (Admin / Platform Owner)
@driver_sub_bp.route('/add', methods=['POST'])
@jwt_required()
def add_driver_subscription():
    try:
        data = request.json

        # ✅ Get user from JWT
        user_id = get_jwt_identity()

        # ✅ Convert User → Driver
        driver = Driver.query.filter_by(UserId=user_id).first()
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        driver_id = driver.Id
        plan_id = data.get('plan_id')

        if not plan_id:
            return jsonify({"error": "plan_id is required"}), 400

        # ✅ Check plan
        from models import SubscriptionPlan
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan or not plan.IsActive:
            return jsonify({"error": "Invalid or inactive plan"}), 400

        # ❌ Prevent multiple active subscriptions
        existing = DriverSubscription.query.filter_by(
            DriverId=driver_id,
            Status='Active'
        ).first()

        if existing:
            return jsonify({
                "error": "You already have an active subscription"
            }), 400

        # ✅ Create subscription (Pending)
        subscription = DriverSubscription(
            DriverId=driver_id,
            PlanId=plan.Id,
            Amount=plan.Price,
            StartDate=datetime.utcnow(),
            EndDate=datetime.utcnow() + timedelta(days=plan.DurationDays),
            Status='Pending'
        )

        db.session.add(subscription)
        db.session.commit()

        return jsonify({
            "message": "Subscription created. Complete payment to activate.",
            "subscription_id": subscription.Id
        }), 201

    except Exception as e:
        db.session.rollback()  # 🔥 important
        return jsonify({"error": str(e)}), 500
    
#List All Subscriptions
@driver_sub_bp.route('/all', methods=['GET'])
@jwt_required()
def list_subscriptions():
    try:
        subscriptions = db.session.query(
            DriverSubscription,
            Driver,
            User
        ).join(Driver, Driver.Id == DriverSubscription.DriverId)\
         .join(User, User.Id == Driver.UserId).all()

        result = []

        for sub, driver, user in subscriptions:
            result.append({
                "id": sub.Id,
                "driver_id": sub.DriverId,
                "driver_name": user.Name,
                "plan_id": sub.PlanId,
                "amount": float(sub.Amount),
                "start_date": sub.StartDate,
                "end_date": sub.EndDate,
                "status": sub.Status
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
            DriverSubscription.DriverId == driver_id
        ).order_by(DriverSubscription.EndDate.desc()).first()

        if not subscription:
            return jsonify({"status": "inactive"})

        # Auto expire
        if subscription.EndDate < datetime.utcnow():
            subscription.Status = 'Expired'
            db.session.commit()
            return jsonify({"status": "expired"})

        return jsonify({
            "status": subscription.Status,
            "start_date": subscription.StartDate,
            "end_date": subscription.EndDate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500