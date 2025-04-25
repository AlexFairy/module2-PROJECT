from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError
from . import inventory_bp
from app.models import Inventory
from app.models import db
from .schemas import inventory_schema, inventory_all_schema

@inventory_bp.route("/", methods=["POST"])
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
        new_inventory = Inventory(
            name=inventory_data["name"],
            price=inventory_data["price"],
            quantity=inventory_data.get("quantity", 0))
        
        db.session.add(new_inventory)
        db.session.commit()
        return jsonify({"id": new_inventory.id,
                        "name": new_inventory.name,
                        "price": new_inventory.price,
                        "quantity": new_inventory.quantity}), 201
    except ValidationError as e:
        return jsonify(e.messages), 400

@inventory_bp.route("/", methods=['GET'])
def get_inventory():
    try:
        inventory_items = db.session.query(Inventory).all()
        inventory_list = [{"id": item.id, "name": item.name, "price": item.price, "quantity": item.quantity} for item in inventory_items]
        return jsonify(inventory_list), 200
    except Exception:
        return jsonify({"message": "Error"}), 500
    
@inventory_bp.route("/search", methods=['GET'])
def search_inventory():
    name = request.args.get("name", "")
    query = select(Inventory).where(Inventory.name.like(f"%{name}%"))
    inventory_items = db.session.execute(query).scalars().all()
    inventory_list = [{"id": item.id, "name": item.name, "price": item.price} for item in inventory_items]
    return jsonify(inventory_list), 200

@inventory_bp.route("/<int:id>", methods=["PUT"])
def update_inventory(id):
    try:
        inventory_item = db.session.query(Inventory).filter_by(id=id).first()
        if not inventory_item:
            return jsonify({"message": "Inventory item not found"}), 404

        inventory_data = inventory_schema.load(request.json)
        inventory_item.name = inventory_data["name"]
        inventory_item.price = inventory_data["price"]
        inventory_item.quantity = inventory_data["quantity"]

        db.session.commit()
        return jsonify({"id": inventory_item.id,
                        "name": inventory_item.name,
                        "price": inventory_item.price,
                        "quantity": inventory_item.quantity}), 200
    except ValidationError as e:
        return jsonify(e.messages), 400
    
@inventory_bp.route("/<int:id>", methods=['DELETE'])
def delete_inventory(id):
    try:
        inventory_item = db.session.query(Inventory).filter_by(id=id).first()
        if not inventory_item:
            return jsonify({"message": "Inventory item not found"}), 404

        db.session.delete(inventory_item)
        db.session.commit()

        return jsonify({"message": f"Inventory item with ID {id} has been deleted"}), 200
    except Exception:
        return jsonify({"message": "Error"}), 500