
USE WTP_DB

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15)   NULL,
    email VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE Drivers (
    Id INT  IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    LicenseNumber NVARCHAR(50),
    VehicleNumber NVARCHAR(20),
    IsVerified BIT DEFAULT 0,
    Rating DECIMAL(2,1) DEFAULT 0,
    TotalTrips INT DEFAULT 0,
    CreatedAt DATETIME,

    CONSTRAINT FK_Drivers_Users FOREIGN KEY (UserId)
        REFERENCES Users(Id) ON DELETE CASCADE
);


CREATE TABLE Tankers (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DriverId INT NOT NULL,
    CapacityLiters INT NOT NULL,
    WaterType VARCHAR(50),
    PricePerTrip DECIMAL(10,2) NOT NULL,
    IsAvailable BIT DEFAULT 1,
    CreatedAt DATETIME,

    CONSTRAINT FK_Tankers_Drivers FOREIGN KEY (DriverId)
        REFERENCES Drivers(Id) ON DELETE CASCADE
);

CREATE TABLE Addresses (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    AddressLine VARCHAR(MAX) NOT NULL,
    City VARCHAR(100),
    State VARCHAR(100),
    Pincode VARCHAR(10),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
    CreatedAt DATETIME,

    CONSTRAINT FK_Addresses_Users FOREIGN KEY (UserId)
        REFERENCES Users(Id) ON DELETE CASCADE
);


CREATE TABLE Bookings (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    TankerId INT NOT NULL,
    AddressId INT NOT NULL,

    Status VARCHAR(20) ,

    ScheduledTime DATETIME,
    DeliveredTime DATETIME,

    TotalPrice DECIMAL(10,2) NOT NULL,
    PaymentStatus VARCHAR(20) ,
    PaymentMethod VARCHAR(20) ,

    CreatedAt DATETIME,

    CONSTRAINT FK_Bookings_Users FOREIGN KEY (UserId) REFERENCES Users(Id),
    CONSTRAINT FK_Bookings_Tankers FOREIGN KEY (TankerId) REFERENCES Tankers(Id),
    CONSTRAINT FK_Bookings_Addresses FOREIGN KEY (AddressId) REFERENCES Addresses(Id)
);

CREATE TABLE DriverLocations (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DriverId INT NOT NULL,
    Latitude DECIMAL(10,7) NOT NULL,
    Longitude DECIMAL(10,7) NOT NULL,
    UpdatedAt DATETIME,

    CONSTRAINT FK_DriverLocations_Drivers FOREIGN KEY (DriverId)
        REFERENCES Drivers(Id) ON DELETE CASCADE
);

CREATE TABLE Payments (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    BookingId INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    PaymentMethod VARCHAR(20) ,
    TransactionId VARCHAR(100),
    Status VARCHAR(20),
    CreatedAt DATETIME,

    CONSTRAINT FK_Payments_Bookings FOREIGN KEY (BookingId)
        REFERENCES Bookings(Id) ON DELETE CASCADE
);

CREATE TABLE Reviews (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    BookingId INT NOT NULL,
    UserId INT NOT NULL,
    DriverId INT NOT NULL,

    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    Comment VARCHAR(MAX),

    CreatedAt DATETIME,

    CONSTRAINT FK_Reviews_Bookings FOREIGN KEY (BookingId) REFERENCES Bookings(Id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Users FOREIGN KEY (UserId) REFERENCES Users(Id),
    CONSTRAINT FK_Reviews_Drivers FOREIGN KEY (DriverId) REFERENCES Drivers(Id)
);


CREATE TABLE Notifications (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Title VARCHAR(255),
    Message VARCHAR(MAX),
    Type VARCHAR(20) CHECK (Type IN ('booking', 'payment', 'alert')),
    IsRead BIT DEFAULT 0,
    CreatedAt DATETIME,

    CONSTRAINT FK_Notifications_Users FOREIGN KEY (UserId)
        REFERENCES Users(Id) ON DELETE CASCADE
);