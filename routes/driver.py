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
        user_id = get_current_user_id()
        data = request.json

        if not data.get('license_number') or not data.get('vehicle_number'):
            return jsonify({"error": "Missing required fields"}), 400

        # ✅ Prevent duplicate
        existing_driver = Driver.query.filter_by(UserId=user_id).first()
        if existing_driver:
            return jsonify({"error": "Driver already exists"}), 409

        driver = Driver(
            UserId=user_id,
            LicenseNumber=data.get('license_number'),
            VehicleNumber=data.get('vehicle_number'),
            VehicleType=data.get('vehicle_type'),
            CreatedAt=datetime.utcnow()
        )

        db.session.add(driver)
        db.session.commit()

        return jsonify({
            "message": "Driver added successfully",
            "driver_id": driver.Id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get All Drivers api
@driver_bp.route('/drivers', methods=['GET'])
def get_drivers():
    try:
        drivers = Driver.query.all()

        return jsonify([
            {
                "id": d.Id,
                "user_id": d.UserId,
                "license_number": d.LicenseNumber,
                "vehicle_number": d.VehicleNumber,
                "vehicle_type": d.VehicleType,
                "is_verified": d.IsVerified,
                "rating": d.Rating,
                "total_trips": d.TotalTrips,
                "status": d.Status
            }
            for d in drivers
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get Single Driver api
@driver_bp.route('/my-driver', methods=['GET'])
@jwt_required()
def get_my_driver():
    try:
        user_id = get_current_user_id()

        driver = Driver.query.filter_by(UserId=user_id).first()

        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        return jsonify({
            "id": driver.Id,
            "user_id": driver.UserId,
            "license_number": driver.LicenseNumber,
            "vehicle_number": driver.VehicleNumber,
            "vehicle_type": driver.VehicleType,
            "is_verified": driver.IsVerified,
            "rating": driver.Rating,
            "total_trips": driver.TotalTrips,
            "status": driver.Status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Update Driver api
@driver_bp.route('/update-driver/<int:driver_id>', methods=['PUT'])
@jwt_required()
def update_driver(driver_id):
    try:
        user_id = get_current_user_id()
        driver = Driver.query.get(driver_id)

        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        # ✅ Only owner can update
        if driver.UserId != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json

        driver.LicenseNumber = data.get('license_number', driver.LicenseNumber)
        driver.VehicleNumber = data.get('vehicle_number', driver.VehicleNumber)
        driver.VehicleType = data.get('vehicle_type', driver.VehicleType)
        driver.IsVerified = data.get('is_verified', driver.IsVerified)
        driver.Rating = data.get('rating', driver.Rating)
        driver.TotalTrips = data.get('total_trips', driver.TotalTrips)
        driver.Status = data.get('status', driver.Status)

        db.session.commit()

        return jsonify({"message": "Driver updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Delete Driver api
@driver_bp.route('/delete-driver/<int:driver_id>', methods=['DELETE'])
@jwt_required()
def delete_driver(driver_id):
    try:
        user_id = get_current_user_id()
        driver = Driver.query.get(driver_id)

        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        # ✅ Only owner can delete
        if driver.UserId != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        db.session.delete(driver)
        db.session.commit()

        return jsonify({"message": "Driver deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500