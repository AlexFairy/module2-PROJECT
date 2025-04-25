from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError
from . import mechanic_bp
from app.models import Mechanic
from app.models import db
from .schemas import mechanic_schema, mechanics_schema

@mechanic_bp.route("/", methods=['POST'])
def create_mechanic():
    print("Incoming request JSON:", request.json)
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanic(
        mechanic_name=mechanic_data["mechanic_name"],
        email=mechanic_data["email"],
        address=mechanic_data["address"],
        phone_number=mechanic_data["phone_number"],
        salary=mechanic_data["salary"]
    )

    db.session.add(new_mechanic)
    db.session.commit()
    print("Mechanic created successfully:", new_mechanic.id)

    return jsonify({"id": new_mechanic.id, "message": "Mechanic added successfully"}), 201

@mechanic_bp.route("/", methods=['GET'])
def get_mechanics():
    try:
        mechanics = db.session.query(Mechanic).all()
        mechanics_list = [{
                "id": mechanic.id,
                "mechanic_name": mechanic.mechanic_name,
                "email": mechanic.email,
                "address": mechanic.address,
                "phone_number": mechanic.phone_number,
                "salary": mechanic.salary} for mechanic in mechanics]
        return jsonify(mechanics_list), 200
    except Exception:
        return jsonify({"message": "Error"}), 500

@mechanic_bp.route("/search", methods=['GET'])
def search_mechanic():
    mechanic_name = request.args.get("mechanic_name", "")
    query = select(Mechanic).where(Mechanic.mechanic_name.like(f"%{mechanic_name}%"))
    mechanics = db.session.execute(query).scalars().all()
    mechanics_list = [{
            "id": mechanic.id,
            "mechanic_name": mechanic.mechanic_name,
            "email": mechanic.email,
            "address": mechanic.address,
            "phone_number": mechanic.phone_number,
            "salary": mechanic.salary} for mechanic in mechanics]
    return jsonify(mechanics_list), 200

@mechanic_bp.route("/<int:id>", methods=['PUT'])
def update_mechanic(id):
    try:
        mechanic = db.session.query(Mechanic).filter_by(id=id).first()
        if not mechanic:
            return jsonify({"message": "Mechanic not found in database! Try a new entry!"}), 404

        try:
            updated_data = mechanic_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400

        mechanic.mechanic_name = updated_data["mechanic_name"]
        mechanic.email = updated_data["email"]
        mechanic.address = updated_data["address"]
        mechanic.phone_number = updated_data["phone_number"]
        mechanic.salary = updated_data["salary"]

        db.session.commit()

        return jsonify({"message": "Mechanic is updated!"}), 200
    except Exception:
        return jsonify({"message": "Error"}), 500

@mechanic_bp.route("/<int:id>", methods=['DELETE'])
def delete_mechanic(id):
    try:
        mechanic = db.session.query(Mechanic).filter_by(id=id).first()
        if not mechanic:
            return jsonify({"message": "Mechanic Data not found"}), 404

        db.session.delete(mechanic)
        db.session.commit()

        return jsonify({"message": f"Mechanic with ID {id} has been deleted"}), 200
    except Exception:
        return jsonify({"message": "Error"}), 500