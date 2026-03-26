from flask import Blueprint, request, jsonify
from models import Review
from helper.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

review_bp = Blueprint('review_bp', __name__)

#Add Review API (User)
@review_bp.route('/add-review', methods=['POST'])
@jwt_required()
def add_review():
    try:
        data = request.json
        user_id = get_jwt_identity()

        booking_id = data.get('booking_id')
        driver_id = data.get('driver_id')
        rating = data.get('rating')
        comment = data.get('comment')

        if not booking_id or not driver_id or not rating:
            return jsonify({"error": "booking_id, driver_id, and rating are required"}), 400

        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        review = Review(
            BookingId=booking_id,
            UserId=user_id,
            DriverId=driver_id,
            Rating=rating,
            Comment=comment,
            CreatedAt=datetime.utcnow()
        )

        db.session.add(review)
        db.session.commit()

        return jsonify({"message": "Review added successfully", "review_id": review.Id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Reviews for a Driver
@review_bp.route('/driver/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_driver_reviews(driver_id):
    try:
        reviews = Review.query.filter_by(DriverId=driver_id).all()
        result = []
        for r in reviews:
            result.append({
                "id": r.Id,
                "booking_id": r.BookingId,
                "user_id": r.UserId,
                "driver_id": r.DriverId,
                "rating": r.Rating,
                "comment": r.Comment,
                "created_at": r.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Get Reviews by User api
@review_bp.route('/my-reviews', methods=['GET'])
@jwt_required()
def my_reviews():
    try:
        user_id = get_jwt_identity()
        reviews = Review.query.filter_by(UserId=user_id).all()
        result = []
        for r in reviews:
            result.append({
                "id": r.Id,
                "booking_id": r.BookingId,
                "driver_id": r.DriverId,
                "rating": r.Rating,
                "comment": r.Comment,
                "created_at": r.CreatedAt
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
