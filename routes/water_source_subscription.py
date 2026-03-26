from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import WaterSourceSubscription, User
from helper.db import db
from datetime import datetime

water_source_sub_bp = Blueprint('water_source_sub_bp', __name__)

#Add Water Source Subscription api
@water_source_sub_bp.route('/add', methods=['POST'])
@jwt_required()
def add_water_source_subscription():
    try:
        data = request.json
        supplier_id = data.get('supplier_id')
        amount = data.get('amount')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not supplier_id or not amount or not start_date or not end_date:
            return jsonify({"error": "supplier_id, amount, start_date, end_date are required"}), 400

        # Check supplier exists and role
        supplier = User.query.get(supplier_id)
        if not supplier or supplier.Role != 'supplier':
            return jsonify({"error": "Supplier not found or invalid role"}), 404

        subscription = WaterSourceSubscription(
            SupplierId=supplier_id,
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
# List All Subscriptions api 
@water_source_sub_bp.route('/all', methods=['GET'])
@jwt_required()
def list_water_source_subscriptions():
    try:
        subscriptions = WaterSourceSubscription.query.all()
        result = []
        for sub in subscriptions:
            supplier = User.query.get(sub.SupplierId)
            result.append({
                "id": sub.Id,
                "supplier_id": sub.SupplierId,
                "supplier_name": supplier.Name if supplier else None,
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
    
#Check Supplier Subscription Status api
@water_source_sub_bp.route('/status/<int:supplier_id>', methods=['GET'])
@jwt_required()
def check_water_source_subscription_status(supplier_id):
    try:
        subscription = WaterSourceSubscription.query.filter(
            WaterSourceSubscription.SupplierId==supplier_id,
            WaterSourceSubscription.Status=='active'
        ).order_by(WaterSourceSubscription.EndDate.desc()).first()

        if not subscription:
            return jsonify({"status": "inactive"})

        return jsonify({
            "status": subscription.Status,
            "start_date": subscription.StartDate,
            "end_date": subscription.EndDate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500