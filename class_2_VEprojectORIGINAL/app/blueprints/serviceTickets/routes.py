from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError
from . import service_ticket_bp
from app.models import ServiceTickets, Inventory, db
from .schemas import service_ticket_schema, service_tickets_schema

@service_ticket_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_ticket = ServiceTickets(
        service_description=ticket_data["service_description"],
        cost=ticket_data["cost"],
        vin_number=ticket_data["vin_number"],
        work_complete=ticket_data["work_complete"],
        car_submission_date=ticket_data["car_submission_date"],
        work_start_date=ticket_data.get("work_start_date"),
        work_finish_date=ticket_data.get("work_finish_date"),
        customer_id=ticket_data["customer_id"],
        mechanic_id=ticket_data["mechanic_id"]
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({"id": new_ticket.id, "message": "Service ticket created successfully!"}), 201


@service_ticket_bp.route("/", methods=['GET'])
def get_service_tickets():
    try:
        tickets = db.session.query(ServiceTickets).all()
        tickets_list = [{
            "id": ticket.id,
            "service_description": ticket.service_description,
            "cost": ticket.cost,
            "vin_number": ticket.vin_number,
            "work_complete": ticket.work_complete,
            "car_submission_date": ticket.car_submission_date.isoformat(),
            "work_start_date": ticket.work_start_date.isoformat() if ticket.work_start_date else None,
            "work_finish_date": ticket.work_finish_date.isoformat() if ticket.work_finish_date else None,
            "inventory_items": [{"id": item.id, "name": item.name, "price": item.price, "quantity": item.quantity}
                                for item in ticket.inventory_items]
        } for ticket in tickets]

        return jsonify(tickets_list), 200
    except Exception:
        return jsonify({"message": "Error"}), 500


@service_ticket_bp.route("/<int:id>/add_part", methods=['POST'])
def add_part_to_service_ticket(id):
    try:
        service_ticket = db.session.query(ServiceTickets).filter_by(id=id).first()
        if not service_ticket:
            return jsonify({"error": "Service ticket not found"}), 404
        
        part_id = request.json.get("part_id")
        inventory_item = db.session.query(Inventory).filter_by(id=part_id).first()
        if not inventory_item:
            return jsonify({"error": "Inventory item not found"}), 404

        if inventory_item.quantity <= 0:
            return jsonify({"error": "Not enough stock"}), 400

        service_ticket.inventory_items.append(inventory_item)
        inventory_item.quantity -= 1 
        db.session.commit()

        return jsonify({"message": f"Part '{inventory_item.name}' added to Service Ticket ID {id}"}), 200
    except Exception as e:
        print(f"Error adding part: {str(e)}")  #  for debug(had issues with this)
        return jsonify({"error": "An error occurred"}), 500


@service_ticket_bp.route("/search", methods=['GET'])
def search_service_ticket():
    vin_number = request.args.get("vin_number", "")
    query = select(ServiceTickets).where(ServiceTickets.vin_number.like(f"%{vin_number}%"))
    tickets = db.session.execute(query).scalars().all()
    tickets_list = [{
        "id": ticket.id,
        "service_description": ticket.service_description,
        "cost": ticket.cost,
        "vin_number": ticket.vin_number,
        "work_complete": ticket.work_complete,
        "car_submission_date": ticket.car_submission_date.isoformat(),
        "work_start_date": ticket.work_start_date.isoformat() if ticket.work_start_date else None,
        "work_finish_date": ticket.work_finish_date.isoformat() if ticket.work_finish_date else None,
        "inventory_items": [{"id": item.id, "name": item.name, "price": item.price, "quantity": item.quantity}
                            for item in ticket.inventory_items]
    } for ticket in tickets]
    return jsonify(tickets_list), 200


@service_ticket_bp.route("/<int:id>", methods=['PUT'])
def update_service_ticket(id):
    print("Incoming ID:", id)
    print("Incoming JSON:", request.json)
    try:
        ticket = db.session.query(ServiceTickets).filter_by(id=id).first()
        if not ticket:
            print("Ticket not found!")  # Debug
            return jsonify({"message": "Service ticket not found! Try again!"}), 404

        try:
            updated_data = service_ticket_schema.load(request.json)
            print("Validated Data:", updated_data)  # for debugging
        except ValidationError as e:
            print("Validation Error:", e.messages)  # for debugging
            return jsonify(e.messages), 400

        ticket.service_description = updated_data["service_description"]
        ticket.cost = updated_data["cost"]
        ticket.vin_number = updated_data["vin_number"]
        ticket.work_complete = updated_data["work_complete"]
        ticket.car_submission_date = updated_data["car_submission_date"]
        ticket.work_start_date = updated_data.get("work_start_date")
        ticket.work_finish_date = updated_data.get("work_finish_date")
        ticket.customer_id = updated_data["customer_id"]
        ticket.mechanic_id = updated_data["mechanic_id"]

        db.session.commit()
        print("Ticket Updated Successfully!")  # same 4 debugging

        return jsonify({"message": "Service ticket updated successfully!!!"}), 200
    except Exception as e:
        print("Exception Occurred:", str(e))  # same 4 debugging
        return jsonify({"message": "Error"}), 500


@service_ticket_bp.route("/<int:id>", methods=['DELETE'])
def delete_service_ticket(id):
    try:
        ticket = db.session.query(ServiceTickets).filter_by(id=id).first()
        if not ticket:
            return jsonify({"message": "Service ticket not in database!"}), 404

        db.session.delete(ticket)
        db.session.commit()

        return jsonify({"message": f"Service ticket with ID {id} has been deleted"}), 200
    except Exception:
        return jsonify({"message": "Error"}), 500
