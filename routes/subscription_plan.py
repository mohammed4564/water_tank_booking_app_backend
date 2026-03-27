from flask import Blueprint, request, jsonify
from helper.db import db
from models import SubscriptionPlan
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
import json

plan_bp = Blueprint('plan_bp', __name__)

#Add Plan API
@plan_bp.route('/add-plan', methods=['POST'])
@jwt_required()
def add_plan():
    try:
        data = request.json

        plan_name = data.get('plan_name')
        price = data.get('price')
        duration = data.get('duration_days')
        features = data.get('features', [])

        # ✅ Validation
        if not plan_name or not price or not duration:
            return jsonify({"error": "Missing required fields"}), 400

        if float(price) <= 0:
            return jsonify({"error": "Price must be greater than 0"}), 400

        # ✅ Duplicate check
        existing = SubscriptionPlan.query.filter_by(PlanName=plan_name).first()
        if existing:
            return jsonify({"error": "Plan already exists"}), 400

        plan = SubscriptionPlan(
            PlanName=plan_name,
            Price=price,
            DurationDays=duration,
            Features=json.dumps(features),
            IsActive=True
        )

        db.session.add(plan)
        db.session.commit()

        return jsonify({
            "message": "Plan added successfully",
            "plan_id": plan.Id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get All Plans
@plan_bp.route('/plans', methods=['GET'])
def get_plans():
    try:
        plans = SubscriptionPlan.query.filter_by(IsActive=True).all()

        return jsonify([{
            "id": p.Id,
            "plan_name": p.PlanName,
            "price": float(p.Price),
            "duration_days": p.DurationDays,
            "features": json.loads(p.Features) if p.Features else [],
            "created_at": p.CreatedAt
        } for p in plans])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get Single Plan
@plan_bp.route('/plan/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    plan = SubscriptionPlan.query.get(plan_id)

    if not plan:
        return jsonify({"error": "Plan not found"}), 404

    return jsonify({
        "id": plan.Id,
        "plan_name": plan.PlanName,
        "price": float(plan.Price),
        "duration_days": plan.DurationDays,
        "features": json.loads(plan.Features) if plan.Features else [],
        "is_active": plan.IsActive
    })

#Update Plan
@plan_bp.route('/update-plan/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    try:
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        data = request.json

        if 'plan_name' in data and data['plan_name']:
            plan.PlanName = data['plan_name']

        if 'price' in data:
            if float(data['price']) <= 0:
                return jsonify({"error": "Invalid price"}), 400
            plan.Price = data['price']

        if 'duration_days' in data:
            plan.DurationDays = data['duration_days']

        if 'features' in data:
            plan.Features = json.dumps(data['features'])

        if 'is_active' in data:
            plan.IsActive = data['is_active']

        db.session.commit()

        return jsonify({"message": "Plan updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Delete Plan (Soft Delete Recommended)
@plan_bp.route('/delete-plan/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    try:
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404

        # Soft delete
        plan.IsActive = False

        db.session.commit()

        return jsonify({"message": "Plan deleted (deactivated) successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500