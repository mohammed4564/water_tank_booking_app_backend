from flask import Blueprint, request, jsonify
from models import Tanker, Driver
from helper.db import db
from flask_jwt_extended import jwt_required
from helper.jwt_handler import get_current_user_id
from datetime import datetime

tanker_bp = Blueprint('tanker_bp', __name__)

# Add Tanker API 

@tanker_bp.route('/add-tanker', methods=['POST'])
@jwt_required()
def add_tanker():
    try:
        data = request.json
        driver_id = data.get('driver_id')

        if not driver_id or not data.get('capacity_liters') or not data.get('price_per_trip'):
            return jsonify({"error": "Missing required fields"}), 400

        tanker = Tanker(
            DriverId=driver_id,
            CapacityLiters=data.get('capacity_liters'),
            WaterType=data.get('water_type'),
            PricePerTrip=data.get('price_per_trip'),
            IsAvailable=True,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(tanker)
        db.session.commit()

        return jsonify({"message": "Tanker added", "tanker_id": tanker.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get All Tankers api

@tanker_bp.route('/tankers', methods=['GET'])
def get_tankers():
    try:
        tankers = Tanker.query.all()
        result = []

        for t in tankers:
            result.append({
                "id": t.Id,
                "driver_id": t.DriverId,
                "capacity_liters": t.CapacityLiters,
                "water_type": t.WaterType,
                "price_per_trip": t.PricePerTrip,
                "is_available": t.IsAvailable
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Single Tanker api

@tanker_bp.route('/tanker/<int:tanker_id>', methods=['GET'])
def get_tanker(tanker_id):
    tanker = Tanker.query.get(tanker_id)
    if not tanker:
        return jsonify({"error": "Tanker not found"}), 404

    return jsonify({
        "id": tanker.Id,
        "driver_id": tanker.DriverId,
        "capacity_liters": tanker.CapacityLiters,
        "water_type": tanker.WaterType,
        "price_per_trip": tanker.PricePerTrip,
        "is_available": tanker.IsAvailable
    })

#Update Tanker api
@tanker_bp.route('/update-tanker/<int:tanker_id>', methods=['PUT'])
@jwt_required()
def update_tanker(tanker_id):
    try:
        tanker = Tanker.query.get(tanker_id)
        if not tanker:
            return jsonify({"error": "Tanker not found"}), 404

        data = request.json
        tanker.CapacityLiters = data.get('capacity_liters', tanker.CapacityLiters)
        tanker.WaterType = data.get('water_type', tanker.WaterType)
        tanker.PricePerTrip = data.get('price_per_trip', tanker.PricePerTrip)
        tanker.IsAvailable = data.get('is_available', tanker.IsAvailable)

        db.session.commit()

        return jsonify({"message": "Tanker updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Delete Tanker api
@tanker_bp.route('/delete-tanker/<int:tanker_id>', methods=['DELETE'])
@jwt_required()
def delete_tanker(tanker_id):
    try:
        tanker = Tanker.query.get(tanker_id)
        if not tanker:
            return jsonify({"error": "Tanker not found"}), 404

        db.session.delete(tanker)
        db.session.commit()

        return jsonify({"message": "Tanker deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
