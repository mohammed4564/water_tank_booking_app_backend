import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def init_db(app):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")

    connection_string = (
        f"mssql+pyodbc://{user}:{password}@{server}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)