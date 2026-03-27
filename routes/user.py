from flask import Blueprint, request, jsonify
from models import User, Role, UserRole, EmailVerification, PhoneVerification
from helper.db import db
import bcrypt, secrets, random
from helper.mail_service import send_email
from datetime import datetime, timedelta
from helper.jwt_handler import generate_access_token, generate_refresh_token, get_current_user_id
from flask_jwt_extended import jwt_required

user_bp = Blueprint('user_bp', __name__)

# --------------------------
# HELPER FUNCTIONS
# --------------------------
def send_email_verification(user):
    """Create & send a new email verification token."""
    # Delete old tokens
    EmailVerification.query.filter_by(UserId=user.Id).delete()

    token = secrets.token_urlsafe(32)
    db.session.add(EmailVerification(
        UserId=user.Id,
        Token=token,
        Expiry=datetime.utcnow() + timedelta(hours=24),
        Status='pending'
    ))
    db.session.commit()

    verify_link = f"http://10.130.29.151:5000/api/users/verify-email?token={token}"
    send_email(
        user.Email,
        "Email Verification",
        f'<h3>Click below to verify your email</h3><a href="{verify_link}">Verify Email</a>'
    )

def create_otp(user):
    """Create a new OTP for phone verification."""
    PhoneVerification.query.filter_by(UserId=user.Id).delete()
    otp = str(random.randint(100000, 999999))
    db.session.add(PhoneVerification(
        UserId=user.Id,
        Otp=otp,
        Expiry=datetime.utcnow() + timedelta(minutes=5),
        Attempts=0,
        Status='pending'
    ))
    db.session.commit()
    print("OTP:", otp)  # Replace with real SMS API
    return otp

# --------------------------
# REGISTER
# --------------------------
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(Email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    user = User(
        Name=data['name'],
        Email=data['email'],
        Phone=data.get('phone'),
        PasswordHash=hashed.decode()
    )
    db.session.add(user)
    db.session.commit()

    # assign default role
    role = Role.query.filter_by(Name='customer').first()
    db.session.add(UserRole(UserId=user.Id, RoleId=role.Id, Status='active'))
    db.session.commit()

    send_email_verification(user)
    return jsonify({"message": "Registered successfully. Check email to verify."}), 201

# --------------------------
# VERIFY EMAIL
# --------------------------
@user_bp.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token missing"}), 400

    record = EmailVerification.query.filter_by(Token=token).first()
    if not record:
        return jsonify({"error": "Invalid token"}), 400

    if record.Status == 'verified':
        return jsonify({"message": "Email already verified"}), 200

    if datetime.utcnow() > record.Expiry:
        record.Status = 'expired'
        db.session.commit()
        return jsonify({"error": "Token expired"}), 400

    record.Status = 'verified'
    db.session.commit()
    return jsonify({"message": "Email verified successfully"}), 200

# --------------------------
# RESEND EMAIL VERIFICATION
# --------------------------
@user_bp.route('/resend-email-verification', methods=['POST'])
def resend_email_verification():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(Email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    send_email_verification(user)
    return jsonify({"message": "Verification link sent"}), 200

# --------------------------
# SEND PHONE OTP
# --------------------------
@user_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    user = User.query.filter_by(Email=data['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = create_otp(user)
    return jsonify({"message": "OTP sent"}), 200

# --------------------------
# RESEND PHONE OTP
# --------------------------
@user_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(Email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if phone already verified
    verified_otp = PhoneVerification.query.filter_by(UserId=user.Id, Status='verified').first()
    if verified_otp:
        return jsonify({"message": "Phone already verified"}), 200

    create_otp(user)
    return jsonify({"message": "OTP resent successfully"}), 200

# --------------------------
# VERIFY OTP
# --------------------------
@user_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    record = PhoneVerification.query.filter_by(
        UserId=data['user_id'],
        Otp=data['otp'],
        Status='pending'
    ).first()

    if not record:
        return jsonify({"error": "Invalid OTP"}), 400

    if datetime.utcnow() > record.Expiry:
        record.Status = 'expired'
        db.session.commit()
        return jsonify({"error": "OTP expired"}), 400

    record.Status = 'verified'
    db.session.commit()
    return jsonify({"message": "Phone verified"}), 200

# --------------------------
# LOGIN
# --------------------------
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(Email=data['email']).first()
    if not user or not bcrypt.checkpw(data['password'].encode(), user.PasswordHash.encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    # Check latest email verification status
    ev = EmailVerification.query.filter_by(UserId=user.Id).order_by(EmailVerification.CreatedAt.desc()).first()
    if not ev or ev.Status != 'verified':
        send_email_verification(user)
        return jsonify({"error": "Email not verified. Verification link resent."}), 403

    # Get active roles
    roles = db.session.query(Role.Name)\
        .join(UserRole, Role.Id == UserRole.RoleId)\
        .filter(UserRole.UserId == user.Id, UserRole.Status=='active').all()
    role_list = [r[0] for r in roles]

    access_token = generate_access_token(user.Id, role=",".join(role_list))
    refresh_token = generate_refresh_token(user.Id)

    return jsonify({
        "id": user.Id,
        "name": user.Name,
        "email": user.Email,
        "phone": user.Phone,
        "roles": role_list,
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# --------------------------
# PROFILE
# --------------------------
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    roles = db.session.query(Role.Name)\
        .join(UserRole, Role.Id == UserRole.RoleId)\
        .filter(UserRole.UserId == user.Id, UserRole.Status=='active').all()
    role_list = [r[0] for r in roles]

    return jsonify({
        "id": user.Id,
        "name": user.Name,
        "email": user.Email,
        "phone": user.Phone,
        "roles": role_list
    }), 200