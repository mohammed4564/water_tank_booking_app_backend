from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from helper.db import db

from models import (
    User, UserRole, Driver,
    DriverSubscription, SubscriptionPayment, SubscriptionPlan
)

admin_bp = Blueprint('admin_bp', __name__)

#FULL DRIVER DETAILS (CLEAN + GROUPED)
@admin_bp.route('/full-driver-details', methods=['GET'])
@jwt_required()
def get_full_driver_details():
    try:
        current_user_id = get_jwt_identity()

        # 🔐 Admin check
        admin_role = UserRole.query.filter_by(UserId=current_user_id).first()

        if not admin_role or admin_role.role_id != 1:
            return jsonify({"error": "Admin only"}), 403

        users = User.query.all()
        result = []

        for user in users:
            # 🔑 User Role
            user_role = UserRole.query.filter_by(user_id=user.id).first()

            # 🚗 Driver
            driver = Driver.query.filter_by(UserId=user.id).first()
            driver_data = None

            if driver:
                subscriptions = DriverSubscription.query.filter_by(
                    DriverId=driver.Id
                ).all()

                subs_list = []

                for sub in subscriptions:
                    plan = SubscriptionPlan.query.get(sub.PlanId)

                    payments = SubscriptionPayment.query.filter_by(
                        SubscriptionId=sub.Id
                    ).all()

                    payment_list = []

                    for pay in payments:
                        payment_list.append({
                            "payment_id": pay.Id,
                            "amount": float(pay.Amount),
                            "payment_method": pay.PaymentMethod,
                            "payment_status": pay.PaymentStatus,
                            "verify_status": pay.VerifyStatus,
                            "transaction_id": pay.TransactionId,
                            "paid_at": pay.PaidAt
                        })

                    subs_list.append({
                        "subscription_id": sub.Id,
                        "status": sub.Status,
                        "start_date": sub.StartDate,
                        "end_date": sub.EndDate,
                        "plan": {
                            "plan_id": plan.Id if plan else None,
                            "plan_name": plan.PlanName if plan else None,
                            "price": float(plan.Price) if plan else None
                        },
                        "payments": payment_list
                    })

                driver_data = {
                    "driver_id": driver.Id,
                    "license_number": driver.LicenseNumber,
                    "vehicle_number": driver.VehicleNumber,
                    "vehicle_type": driver.VehicleType,
                    "subscriptions": subs_list
                }

            result.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
                "role_status": user_role.status if user_role else None,
                "driver": driver_data
            })

        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
# UPDATED APPROVE API for driver 
@admin_bp.route('/approve-driver-full/<int:user_id>', methods=['PUT'])
@jwt_required()
def approve_driver_full(user_id):
    try:
        current_user_id = get_jwt_identity()

        # 🔐 Admin check
        admin_role = UserRole.query.filter_by(user_id=current_user_id).first()
        if not admin_role or admin_role.role_id != 1:
            return jsonify({"error": "Admin only"}), 403

        # 🔑 USER ROLE
        user_role = UserRole.query.filter_by(user_id=user_id).first()
        if not user_role:
            return jsonify({"error": "User role not found"}), 404

        user_role.status = 'Approved'
        user_role.role_id = 2  # Driver role

        # 🚗 DRIVER
        driver = Driver.query.filter_by(UserId=user_id).first()

        if not driver:
            driver = Driver(
                UserId=user_id,
                Status='Active',
                IsVerified=True
            )
            db.session.add(driver)
            db.session.flush()  # get driver.Id
        else:
            driver.Status = 'Active'
            driver.IsVerified = True

        # 📦 SUBSCRIPTIONS
        subscriptions = DriverSubscription.query.filter_by(
            DriverId=driver.Id
        ).all()

        for sub in subscriptions:
            sub.Status = 'Active'

            # 💳 PAYMENTS
            payments = SubscriptionPayment.query.filter_by(
                SubscriptionId=sub.Id
            ).all()

            for pay in payments:
                pay.VerifyStatus = 'Approved'
                pay.PaymentStatus = 'Paid'

        db.session.commit()

        return jsonify({
            "message": "Driver fully approved and all statuses updated"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
#WHEN ADMIN REJECTS api
@admin_bp.route('/reject-driver-full/<int:user_id>', methods=['PUT'])
@jwt_required()
def reject_driver_full(user_id):
    try:
        current_user_id = get_jwt_identity()

        admin_role = UserRole.query.filter_by(user_id=current_user_id).first()
        if not admin_role or admin_role.role_id != 1:
            return jsonify({"error": "Admin only"}), 403

        user_role = UserRole.query.filter_by(user_id=user_id).first()
        if not user_role:
            return jsonify({"error": "User role not found"}), 404

        user_role.status = 'Rejected'
        user_role.role_id = 3  # back to normal user

        driver = Driver.query.filter_by(UserId=user_id).first()
        if driver:
            driver.Status = 'Inactive'
            driver.IsVerified = False

        subscriptions = DriverSubscription.query.filter_by(
            DriverId=driver.Id
        ).all() if driver else []

        for sub in subscriptions:
            sub.Status = 'Rejected'

            payments = SubscriptionPayment.query.filter_by(
                SubscriptionId=sub.Id
            ).all()

            for pay in payments:
                pay.VerifyStatus = 'Rejected'

        db.session.commit()

        return jsonify({"message": "Driver rejected successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500