from flask import Blueprint, request, jsonify
from models import DriverLocation
from helper.db import db
from flask_jwt_extended import jwt_required
from datetime import datetime

driver_location_bp = Blueprint('driver_location_bp', __name__)

#Update Driver Location API
@driver_location_bp.route('/update-location', methods=['POST'])
@jwt_required()
def update_location():
    try:
        data = request.json
        driver_id = data.get('driver_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not driver_id or latitude is None or longitude is None:
            return jsonify({"error": "driver_id, latitude, and longitude are required"}), 400

        # Check if a record already exists for this driver
        location = DriverLocation.query.filter_by(DriverId=driver_id).first()
        if location:
            location.Latitude = latitude
            location.Longitude = longitude
            location.UpdatedAt = datetime.utcnow()
        else:
            location = DriverLocation(
                DriverId=driver_id,
                Latitude=latitude,
                Longitude=longitude,
                UpdatedAt=datetime.utcnow()
            )
            db.session.add(location)

        db.session.commit()

        return jsonify({"message": "Location updated successfully", "driver_id": driver_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Driver Location API
@driver_location_bp.route('/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_location(driver_id):
    try:
        location = DriverLocation.query.filter_by(DriverId=driver_id).first()
        if not location:
            return jsonify({"error": "Location not found"}), 404

        return jsonify({
            "driver_id": location.DriverId,
            "latitude": location.Latitude,
            "longitude": location.Longitude,
            "updated_at": location.UpdatedAt
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    