from flask import Blueprint, request, jsonify
from models import Address
from helper.db import db
from flask_jwt_extended import jwt_required
from helper.jwt_handler import get_current_user_id
from datetime import datetime

address_bp = Blueprint('address_bp', __name__)

# add address api
@address_bp.route('/add-address', methods=['POST'])
@jwt_required()
def add_address():
    try:
        user_id = get_current_user_id()
        data = request.json

        if not data.get('address_line'):
            return jsonify({"error": "Address is required"}), 400

        address = Address(
            UserId=user_id,
            AddressLine=data.get('address_line'),
            City=data.get('city'),
            State=data.get('state'),
            Pincode=data.get('pincode'),
            Latitude=float(data.get('latitude')) if data.get('latitude') else None,
            Longitude=float(data.get('longitude')) if data.get('longitude') else None
            )   

        db.session.add(address)
        db.session.commit()

        return jsonify({
            "message": "Address added successfully",
            "address_id": address.Id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# GET MY ADDRESSES
@address_bp.route('/my-addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    try:
        user_id = get_current_user_id()

        addresses = Address.query.filter_by(UserId=user_id).all()

        result = []
        for a in addresses:
            result.append({
                "id": a.Id,
                "address": a.AddressLine,
                "city": a.City,
                "state": a.State,
                "pincode": a.Pincode,
                "latitude": a.Latitude,
                "longitude": a.Longitude
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# UPDATE ADDRESS api

@address_bp.route('/update-address/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    try:
        user_id = get_current_user_id()
        data = request.json

        address = Address.query.filter_by(Id=address_id, UserId=user_id).first()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        address.AddressLine = data.get('address_line', address.AddressLine)
        address.City = data.get('city', address.City)
        address.State = data.get('state', address.State)
        address.Pincode = data.get('pincode', address.Pincode)
        address.Latitude = data.get('latitude', address.Latitude)
        address.Longitude = data.get('longitude', address.Longitude)

        db.session.commit()

        return jsonify({"message": "Address updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# DELETE ADDRESS api
@address_bp.route('/delete-address/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    try:
        user_id = get_current_user_id()

        address = Address.query.filter_by(Id=address_id, UserId=user_id).first()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        db.session.delete(address)
        db.session.commit()

        return jsonify({"message": "Address deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500