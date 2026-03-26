from flask import Blueprint, request, jsonify
from helper.db import db
from models import SubscriptionPlan
from flask_jwt_extended import jwt_required
import json

plan_bp = Blueprint('plan_bp', __name__)

#Add Plan API
@plan_bp.route('/add-plan', methods=['POST'])
@jwt_required()
def add_plan():
    try:
        data = request.json

        if not data.get('plan_name') or not data.get('price') or not data.get('duration_days'):
            return jsonify({"error": "Missing required fields"}), 400

        plan = SubscriptionPlan(
            PlanName=data.get('plan_name'),
            Price=data.get('price'),
            DurationDays=data.get('duration_days'),
            Features=json.dumps(data.get('features')) if data.get('features') else None
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
        result = []

        for p in plans:
            result.append({
                "id": p.Id,
                "plan_name": p.PlanName,
                "price": float(p.Price),
                "duration_days": p.DurationDays,
                "features": json.loads(p.Features) if p.Features else [],
                "is_active": p.IsActive
            })

        return jsonify(result)

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

        plan.PlanName = data.get('plan_name', plan.PlanName)
        plan.Price = data.get('price', plan.Price)
        plan.DurationDays = data.get('duration_days', plan.DurationDays)

        if data.get('features'):
            plan.Features = json.dumps(data.get('features'))

        plan.IsActive = data.get('is_active', plan.IsActive)

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