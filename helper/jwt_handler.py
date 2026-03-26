from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()

# 🔒 In-memory blacklist (for dev)
# 👉 In production use Redis / DB
blacklist = set()


# 🔧 Initialize JWT
def init_jwt(app):
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    jwt.init_app(app)

    # 🔴 Missing token
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {"error": "Missing Authorization Header"}, 401

    # 🔴 Invalid token
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {"error": "Invalid Token"}, 401

    # 🔴 Expired token
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": "Token Expired"}, 401

    # 🔴 Revoked token
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"error": "Token Revoked"}, 401

    # 🔴 Check blacklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in blacklist


# 🔑 Generate Access Token (with role)
def generate_access_token(user_id, role="customer"):
    return create_access_token(
        identity=str(user_id),
        additional_claims={"role": role}
    )


# 🔄 Generate Refresh Token
def generate_refresh_token(user_id):
    return create_refresh_token(identity=str(user_id))


# 🔍 Get Current User ID
def get_current_user_id():
    identity = get_jwt_identity()
    return int(identity) if identity else None


# 👮 Get Role from Token
def get_current_user_role():
    claims = get_jwt()
    return claims.get("role")


# 🔁 Refresh Token
def refresh_user_token():
    identity = get_jwt_identity()
    claims = get_jwt()
    return create_access_token(
        identity=identity,
        additional_claims={"role": claims.get("role")}
    )


# 🚪 Logout (Blacklist token)
def logout_user():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return {"message": "Logged out successfully"}