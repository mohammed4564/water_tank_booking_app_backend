from flask import Blueprint, request, jsonify
from models import Driver, User
from helper.db import db
from flask_jwt_extended import jwt_required
from helper.jwt_handler import get_current_user_id
from datetime import datetime

driver_bp = Blueprint('driver_bp', __name__)

#Add Driver API
@driver_bp.route('/add-driver', methods=['POST'])
@jwt_required()
def add_driver():
    try:
        data = request.json
        user_id = get_current_user_id()

        if not user_id or not data.get('license_number') or not data.get('vehicle_number'):
            return jsonify({"error": "Missing required fields"}), 400

        driver = Driver(
            UserId=user_id,
            LicenseNumber=data.get('license_number'),
            VehicleNumber=data.get('vehicle_number'),
            VehicleType=data.get('vehicle_type'),  # ✅ NEW
            CreatedAt=datetime.utcnow()
        )

        db.session.add(driver)
        db.session.commit()

        return jsonify({
            "message": "Driver added",
            "driver_id": driver.Id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get All Drivers api
@driver_bp.route('/drivers', methods=['GET'])
def get_drivers():
    try:
        drivers = Driver.query.all()
        result = []

        for d in drivers:
            result.append({
                "id": d.Id,
                "user_id": d.UserId,
                "license_number": d.LicenseNumber,
                "vehicle_number": d.VehicleNumber,
                "vehicle_type": d.VehicleType,  # ✅ NEW
                "is_verified": d.IsVerified,
                "rating": d.Rating,
                "total_trips": d.TotalTrips
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get Single Driver api
@driver_bp.route('/driver/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    return jsonify({
        "id": driver.Id,
        "user_id": driver.UserId,
        "license_number": driver.LicenseNumber,
        "vehicle_number": driver.VehicleNumber,
        "vehicle_type": driver.VehicleType,  # ✅ NEW
        "is_verified": driver.IsVerified,
        "rating": driver.Rating,
        "total_trips": driver.TotalTrips
    })
# Update Driver api
@driver_bp.route('/update-driver/<int:driver_id>', methods=['PUT'])
@jwt_required()
def update_driver(driver_id):
    try:
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        data = request.json

        driver.LicenseNumber = data.get('license_number', driver.LicenseNumber)
        driver.VehicleNumber = data.get('vehicle_number', driver.VehicleNumber)
        driver.VehicleType = data.get('vehicle_type', driver.VehicleType)  # ✅ NEW
        driver.IsVerified = data.get('is_verified', driver.IsVerified)
        driver.Rating = data.get('rating', driver.Rating)
        driver.TotalTrips = data.get('total_trips', driver.TotalTrips)

        db.session.commit()

        return jsonify({"message": "Driver updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Delete Driver api
@driver_bp.route('/delete-driver/<int:driver_id>', methods=['DELETE'])
@jwt_required()
def delete_driver(driver_id):
    try:
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        db.session.delete(driver)
        db.session.commit()

        return jsonify({"message": "Driver deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500