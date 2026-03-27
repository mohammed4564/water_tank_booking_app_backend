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

        from models import Role

        admin_role_data = Role.query.filter_by(Name='Admin').first()

        if not admin_role_data:
            return jsonify({"error": "Admin role not found"}), 500

        admin_role = UserRole.query.filter_by(UserId=current_user_id).first()

        if not admin_role or admin_role.RoleId != admin_role_data.Id:
            return jsonify({"error": "Admin only"}), 403

        result = []

        # ✅ ONLY USERS WHO ARE DRIVERS
        drivers = Driver.query.all()

        for driver in drivers:

            user = User.query.get(driver.UserId)
            if not user:
                continue

            user_role = UserRole.query.filter_by(UserId=user.Id).first()

            subscriptions = DriverSubscription.query.filter_by(
                DriverId=driver.Id
            ).all()

            # ❌ SKIP IF NO SUBSCRIPTION
            if not subscriptions:
                continue

            subs_list = []

            for sub in subscriptions:

                payments = SubscriptionPayment.query.filter_by(
                    SubscriptionId=sub.Id
                ).all()

                # ❌ IMPORTANT: ONLY INCLUDE PAID USERS
                if not payments:
                    continue

                plan = SubscriptionPlan.query.get(sub.PlanId)

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

            # ❌ SKIP IF NO VALID PAYMENT SUBSCRIPTION
            if not subs_list:
                continue

            result.append({
                "user": {
                    "user_id": user.Id,
                    "name": user.Name,
                    "email": user.Email,
                    "phone": user.Phone,
                    "is_active": user.IsActive,
                    "role_status": user_role.Status if user_role else None
                },
                "driver": {
                    "driver_id": driver.Id,
                    "license_number": driver.LicenseNumber,
                    "vehicle_number": driver.VehicleNumber,
                    "vehicle_type": driver.VehicleType,
                    "is_verified": driver.IsVerified,
                    "status": driver.Status
                },
                "subscriptions": subs_list
            })

        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    


#APPROVE DRIVER API (FINAL FIX)
@admin_bp.route('/approve-driver-full/<int:user_id>', methods=['PUT'])
@jwt_required()
def approve_driver_full(user_id):
    try:
        current_user_id = get_jwt_identity()

        from models import Role

        # 🔐 Roles
        admin_role_data = Role.query.filter_by(Name='Admin').first()
        driver_role_data = Role.query.filter_by(Name='Driver').first()

        if not admin_role_data or not driver_role_data:
            return jsonify({"error": "Roles not configured"}), 500

        # 🔐 Admin check
        admin_role = UserRole.query.filter_by(UserId=current_user_id).first()
        if not admin_role or admin_role.RoleId != admin_role_data.Id:
            return jsonify({"error": "Admin only"}), 403

        # 🔑 User role
        user_role = UserRole.query.filter_by(UserId=user_id).first()
        if not user_role:
            return jsonify({"error": "User role not found"}), 404

        user_role.Status = 'Approved'
        user_role.RoleId = driver_role_data.Id

        # 🚗 Driver
        driver = Driver.query.filter_by(UserId=user_id).first()

        if not driver:
            driver = Driver(
                UserId=user_id,
                Status='Active',
                IsVerified=True
            )
            db.session.add(driver)
            db.session.flush()
        else:
            driver.Status = 'Active'
            driver.IsVerified = True

        # 📦 Subscriptions (SAFE CHECK)
        subscriptions = DriverSubscription.query.filter_by(
            DriverId=driver.Id
        ).all() if driver else []

        for sub in subscriptions:
            sub.Status = 'Active'

            payments = SubscriptionPayment.query.filter_by(
                SubscriptionId=sub.Id
            ).all()

            for pay in payments:
                pay.VerifyStatus = 'Approved'
                pay.PaymentStatus = 'Paid'

        db.session.commit()

        return jsonify({
            "message": "Driver fully approved successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
 
#REJECT DRIVER API (FINAL FIX)
@admin_bp.route('/reject-driver-full/<int:user_id>', methods=['PUT'])
@jwt_required()
def reject_driver_full(user_id):
    try:
        current_user_id = get_jwt_identity()

        from models import Role

        # 🔐 Roles
        admin_role_data = Role.query.filter_by(Name='Admin').first()
        user_role_data = Role.query.filter_by(Name='User').first()

        if not admin_role_data or not user_role_data:
            return jsonify({"error": "Roles not configured"}), 500

        # 🔐 Admin check
        admin_role = UserRole.query.filter_by(UserId=current_user_id).first()
        if not admin_role or admin_role.RoleId != admin_role_data.Id:
            return jsonify({"error": "Admin only"}), 403

        # 🔑 User role
        user_role = UserRole.query.filter_by(UserId=user_id).first()
        if not user_role:
            return jsonify({"error": "User role not found"}), 404

        user_role.Status = 'Rejected'
        user_role.RoleId = user_role_data.Id

        # 🚗 Driver
        driver = Driver.query.filter_by(UserId=user_id).first()

        if driver:
            driver.Status = 'Inactive'
            driver.IsVerified = False

            # 📦 Subscriptions
            subscriptions = DriverSubscription.query.filter_by(
                DriverId=driver.Id
            ).all()

            for sub in subscriptions:
                sub.Status = 'Rejected'

                # 💳 Payments
                payments = SubscriptionPayment.query.filter_by(
                    SubscriptionId=sub.Id
                ).all()

                for pay in payments:
                    pay.VerifyStatus = 'Rejected'
                    pay.PaymentStatus = 'Failed'

        db.session.commit()

        return jsonify({
            "message": "Driver rejected successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500