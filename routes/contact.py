from flask import Blueprint, request, jsonify
from models import ContactUs
from helper.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

contact_bp = Blueprint('contact_bp', __name__)

# Send Query API (User/Guest) api 
@contact_bp.route('/send-query', methods=['POST'])
@jwt_required(optional=True)  # allows guest users
def send_query():
    try:
        data = request.json
        user_id = get_jwt_identity()  # None if guest

        # Required fields
        if not data.get('name') or not data.get('email') or not data.get('message'):
            return jsonify({"error": "Name, email and message are required"}), 400

        query = ContactUs(
            UserId=user_id,
            Name=data.get('name'),
            Email=data.get('email'),
            Phone=data.get('phone'),           # mobile number
            Subject=data.get('subject'),
            Message=data.get('message'),
            CreatedAt=datetime.utcnow()
        )

        db.session.add(query)
        db.session.commit()

        return jsonify({"message": "Query submitted successfully", "query_id": query.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Get All Queries API (Admin)
@contact_bp.route('/queries', methods=['GET'])
@jwt_required()
def get_queries():
    try:
        queries = ContactUs.query.all()
        result = []
        for q in queries:
            result.append({
                "id": q.Id,
                "user_id": q.UserId,
                "name": q.Name,
                "email": q.Email,
                "phone": q.Phone,
                "subject": q.Subject,
                "message": q.Message,
                "status": q.Status,
                "created_at": q.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Update Query Status API (Admin) 
@contact_bp.route('/update-query/<int:query_id>', methods=['PUT'])
@jwt_required()
def update_query(query_id):
    try:
        query = ContactUs.query.get(query_id)
        if not query:
            return jsonify({"error": "Query not found"}), 404

        data = request.json
        query.Status = data.get('status', query.Status)  # pending or resolved

        db.session.commit()
        return jsonify({"message": "Query status updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500