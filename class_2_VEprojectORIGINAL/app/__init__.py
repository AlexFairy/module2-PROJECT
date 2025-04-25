from flask import Flask
from app.models import db
from app.extensions import limiter, cache, ma
from app.blueprints.customers import customer_bp
from app.blueprints.mechanics import mechanic_bp
from app.blueprints.serviceTickets import service_ticket_bp
from app.blueprints.inventory import inventory_bp
from config import DevelopmentConfig, TestingConfig


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}

def create_app(config_name):
    app = Flask(__name__)
    config_class = config_by_name.get(config_name.lower())
    if not config_class:
        raise ValueError(f"Invalid configuration name: {config_name}")
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(customer_bp, url_prefix="/customers", name="customer_bp")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics", name="mechanic_bp")
    app.register_blueprint(service_ticket_bp, url_prefix="/service_tickets", name="service_ticket_bp")
    app.register_blueprint(inventory_bp, url_prefix="/inventory", name="inventory_bp")

    return app