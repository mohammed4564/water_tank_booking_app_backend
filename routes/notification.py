from flask import Blueprint, request, jsonify
from models import Notification
from helper.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

notification_bp = Blueprint('notification_bp', __name__)

#Send Notification API (Admin) api
@notification_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    try:
        data = request.json
        user_id = data.get('user_id')
        title = data.get('title')
        message = data.get('message')
        type_ = data.get('type', 'alert')  # default to alert

        if not user_id or not title or not message:
            return jsonify({"error": "user_id, title, and message are required"}), 400

        notification = Notification(
            UserId=user_id,
            Title=title,
            Message=message,
            Type=type_,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(notification)
        db.session.commit()

        return jsonify({"message": "Notification sent", "notification_id": notification.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Get User Notifications api
@notification_bp.route('/my-notifications', methods=['GET'])
@jwt_required()
def my_notifications():
    try:
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(UserId=user_id).order_by(Notification.CreatedAt.desc()).all()

        result = []
        for n in notifications:
            result.append({
                "id": n.Id,
                "title": n.Title,
                "message": n.Message,
                "type": n.Type,
                "is_read": n.IsRead,
                "created_at": n.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Mark Notification as Read api
@notification_bp.route('/mark-read/<int:notification_id>', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        notification.IsRead = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
