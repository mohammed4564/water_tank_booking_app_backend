from helper.db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    Id = db.Column('id', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(100))
    Phone = db.Column('phone', db.String(15))
    Email = db.Column('email', db.String(100), unique=True)
    PasswordHash = db.Column('password_hash', db.Text)
    CreatedAt = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    IsActive = db.Column('is_active', db.Boolean, default=True)


class Role(db.Model):
    __tablename__ = 'roles'

    Id = db.Column('id', db.Integer, primary_key=True)
    Name = db.Column('name', db.String(50), unique=True)


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    Id = db.Column('id', db.Integer, primary_key=True)
    UserId = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    RoleId = db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
    Status = db.Column('status', db.String(20), default='active')  # active / inactive / pending


class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    Id = db.Column('id', db.Integer, primary_key=True)
    UserId = db.Column('user_id', db.Integer)
    Token = db.Column('token', db.String(255))
    Expiry = db.Column('expiry', db.DateTime)
    Status = db.Column('status', db.String(20), default='pending')  # pending / verified / expired
    CreatedAt = db.Column('created_at', db.DateTime, default=datetime.utcnow)


class PhoneVerification(db.Model):
    __tablename__ = 'phone_verifications'

    Id = db.Column('id', db.Integer, primary_key=True)
    UserId = db.Column('user_id', db.Integer)
    Otp = db.Column('otp', db.String(10))
    Expiry = db.Column('expiry', db.DateTime)
    Attempts = db.Column('attempts', db.Integer, default=0)
    Status = db.Column('status', db.String(20), default='pending')  # pending / verified / expired
    CreatedAt = db.Column('created_at', db.DateTime, default=datetime.utcnow)

class Address(db.Model):
    __tablename__ = 'Addresses'

    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'))
    AddressLine = db.Column(db.String)
    City = db.Column(db.String(100))
    State = db.Column(db.String(100))
    Pincode = db.Column(db.String(10))
    Latitude = db.Column(db.Float)
    Longitude = db.Column(db.Float)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ add here

class Driver(db.Model):
    __tablename__ = 'Drivers'

    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'))
    LicenseNumber = db.Column(db.String)
    VehicleNumber = db.Column(db.String)
    VehicleType = db.Column(db.String(50))
    IsVerified = db.Column(db.Boolean, default=False)
    Rating = db.Column(db.Float, default=0)
    TotalTrips = db.Column(db.Integer, default=0)
    Status = db.Column(db.String(20), default='Active')  # ✅ NEW
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)


class Tanker(db.Model):
    __tablename__ = 'Tankers'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    DriverId = db.Column(
        db.Integer,
        db.ForeignKey('Drivers.Id', ondelete='CASCADE'),
        nullable=False
    )

    CapacityLiters = db.Column(db.Integer, nullable=False)

    WaterType = db.Column(db.String(50), nullable=True)

    PricePerTrip = db.Column(db.Numeric(10, 2), nullable=False)

    IsAvailable = db.Column(db.Boolean, default=True)

    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    driver = db.relationship(
        'Driver',
        backref=db.backref('tankers', passive_deletes=True),
        lazy=True
    )

class Booking(db.Model):
    __tablename__ = 'Bookings'

    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'))
    TankerId = db.Column(db.Integer, db.ForeignKey('Tankers.Id'))
    AddressId = db.Column(db.Integer, db.ForeignKey('Addresses.Id'))

    Status = db.Column(db.String(20), default="pending")
    ScheduledTime = db.Column(db.DateTime)
    DeliveredTime = db.Column(db.DateTime)

    TotalPrice = db.Column(db.Float)
    PaymentStatus = db.Column(db.String(20))
    PaymentMethod = db.Column(db.String(20))

    CreatedAt = db.Column(db.DateTime)

class ContactUs(db.Model):
    __tablename__ = 'ContactUs'

    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(15))            # added phone field
    Subject = db.Column(db.String(255))
    Message = db.Column(db.Text, nullable=False)
    Status = db.Column(db.String(20), default='pending')
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'Notifications'

    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    Title = db.Column(db.String(255))
    Message = db.Column(db.Text)
    Type = db.Column(db.String(20))  # booking, payment, alert
    IsRead = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
class Review(db.Model):
    __tablename__ = 'Reviews'

    Id = db.Column(db.Integer, primary_key=True)
    BookingId = db.Column(db.Integer, db.ForeignKey('Bookings.Id'), nullable=False)
    UserId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    DriverId = db.Column(db.Integer, db.ForeignKey('Drivers.Id'), nullable=False)
    Rating = db.Column(db.Integer, nullable=False)  # 1-5
    Comment = db.Column(db.Text)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class DriverLocation(db.Model):
    __tablename__ = 'DriverLocations'

    Id = db.Column(db.Integer, primary_key=True)
    DriverId = db.Column(db.Integer, db.ForeignKey('Drivers.Id'), nullable=False)
    Latitude = db.Column(db.Float, nullable=False)
    Longitude = db.Column(db.Float, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'Payments'

    Id = db.Column(db.Integer, primary_key=True)
    BookingId = db.Column(db.Integer, db.ForeignKey('Bookings.Id'), nullable=False)
    Amount = db.Column(db.Float, nullable=False)
    PaymentMethod = db.Column(db.String(20))
    TransactionId = db.Column(db.String(100))
    Status = db.Column(db.String(20))  # pending, completed, failed
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class WaterPrice(db.Model):
    __tablename__ = 'WaterPrices'

    Id = db.Column(db.Integer, primary_key=True)
    VehicleType = db.Column(db.String(50), nullable=False)   # Tank, Mini Truck, Line Truck
    WaterType = db.Column(db.String(50), nullable=False)     # Drinking, RO, Mineral
    CapacityLiters = db.Column(db.Integer, nullable=False)   # 5, 20, etc.
    PricePerTrip = db.Column(db.Float, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Bill(db.Model):
    __tablename__ = 'Bills'

    Id = db.Column(db.Integer, primary_key=True)
    BookingId = db.Column(db.Integer, db.ForeignKey('Bookings.Id'), nullable=False)
    PaymentId = db.Column(db.Integer, db.ForeignKey('Payments.Id'), nullable=False)
    BillData = db.Column(db.Text, nullable=False)  # JSON string
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, onupdate=datetime.utcnow)
class SubscriptionPayment(db.Model):
    __tablename__ = 'SubscriptionPayments'

    Id = db.Column(db.Integer, primary_key=True)

    SubscriptionId = db.Column(
        db.Integer,
        db.ForeignKey('DriverSubscriptions.Id', ondelete='CASCADE'),
        nullable=False
    )

    Amount = db.Column(db.Numeric(10, 2), nullable=False)

    PaymentMethod = db.Column(db.String(50), nullable=False)

    PaymentStatus = db.Column(db.String(20), default='Pending')

    TransactionId = db.Column(db.String(100))

    PaidAt = db.Column(db.DateTime)

    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relationship (clean naming)
    subscription = db.relationship(
        'DriverSubscription',
        backref=db.backref('payment_records', lazy=True),
        lazy=True
    )
class SubscriptionPlan(db.Model):
    __tablename__ = 'SubscriptionPlans'

    Id = db.Column(db.Integer, primary_key=True)

    PlanName = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    Features = db.Column(db.Text)
    DurationDays = db.Column(db.Integer, nullable=False)
    IsActive = db.Column(db.Boolean, default=True)

    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relationship
    subscriptions = db.relationship('DriverSubscription', backref='plan', lazy=True)

class DriverSubscription(db.Model):
    __tablename__ = 'DriverSubscriptions'

    Id = db.Column(db.Integer, primary_key=True)

    DriverId = db.Column(
        db.Integer,
        db.ForeignKey('Drivers.Id'),
        nullable=False
    )

    # 🔥 NEW (VERY IMPORTANT)
    PlanId = db.Column(
        db.Integer,
        db.ForeignKey('SubscriptionPlans.Id'),
        nullable=False
    )

    Amount = db.Column(db.Numeric(10, 2), nullable=False)

    StartDate = db.Column(db.DateTime, nullable=False)
    EndDate = db.Column(db.DateTime, nullable=False)

    Status = db.Column(db.String(20), default='Pending')  # Pending, Active, Expired

    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 🔗 Relationship
    payments = db.relationship(
        'SubscriptionPayment',
        backref='driver_subscription',
        cascade='all, delete',
        passive_deletes=True
    )

class WaterSourceSubscription(db.Model):
    __tablename__ = 'WaterSourceSubscriptions'

    Id = db.Column(db.Integer, primary_key=True)
    SupplierId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)  # User with role='supplier'
    Amount = db.Column(db.Float, nullable=False)  # subscription amount
    StartDate = db.Column(db.DateTime, nullable=False)
    EndDate = db.Column(db.DateTime, nullable=False)
    Status = db.Column(db.String(20), default='active')  # active / expired
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, onupdate=datetime.utcnow)