from flask import Blueprint, request, jsonify
from models import WaterPrice
from helper.db import db
from flask_jwt_extended import jwt_required
from datetime import datetime

water_price_bp = Blueprint('water_price_bp', __name__)
#Add Water Price (Admin) api
@water_price_bp.route('/add', methods=['POST'])
@jwt_required()
def add_water_price():
    try:
        data = request.json
        vehicle = data.get('vehicle_type')
        water_type = data.get('water_type')
        capacity = data.get('capacity_liters')
        price = data.get('price_per_trip')

        if not vehicle or not water_type or capacity is None or price is None:
            return jsonify({"error": "vehicle_type, water_type, capacity_liters, and price_per_trip are required"}), 400

        water_price = WaterPrice(
            VehicleType=vehicle,
            WaterType=water_type,
            CapacityLiters=capacity,
            PricePerTrip=price,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(water_price)
        db.session.commit()
        return jsonify({"message": "Water price added", "id": water_price.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get All Water Prices
@water_price_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_prices():
    try:
        prices = WaterPrice.query.all()
        result = []
        for p in prices:
            result.append({
                "id": p.Id,
                "vehicle_type": p.VehicleType,
                "water_type": p.WaterType,
                "capacity_liters": p.CapacityLiters,
                "price_per_trip": p.PricePerTrip,
                "created_at": p.CreatedAt,
                "updated_at": p.UpdatedAt
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Update Water Price api
@water_price_bp.route('/update/<int:price_id>', methods=['PUT'])
@jwt_required()
def update_price(price_id):
    try:
        data = request.json
        price = WaterPrice.query.get(price_id)
        if not price:
            return jsonify({"error": "Price record not found"}), 404

        price.VehicleType = data.get('vehicle_type', price.VehicleType)
        price.WaterType = data.get('water_type', price.WaterType)
        price.CapacityLiters = data.get('capacity_liters', price.CapacityLiters)
        price.PricePerTrip = data.get('price_per_trip', price.PricePerTrip)
        price.UpdatedAt = datetime.utcnow()

        db.session.commit()
        return jsonify({"message": "Water price updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Fetch Price for a Specific Vehicle + Water + Capacity api

@water_price_bp.route('/get-price', methods=['POST'])
@jwt_required()
def get_price():
    try:
        data = request.json
        vehicle = data.get('vehicle_type')
        water_type = data.get('water_type')
        capacity = data.get('capacity_liters')

        price = WaterPrice.query.filter_by(
            VehicleType=vehicle,
            WaterType=water_type,
            CapacityLiters=capacity
        ).first()

        if not price:
            return jsonify({"error": "Price not found"}), 404

        return jsonify({
            "vehicle_type": price.VehicleType,
            "water_type": price.WaterType,
            "capacity_liters": price.CapacityLiters,
            "price_per_trip": price.PricePerTrip
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
