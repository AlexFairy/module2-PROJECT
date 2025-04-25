
from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError
from . import customer_bp
from app.models import Customers, db
from app.blueprints.serviceTickets.schemas import ServiceTickets
from .schemas import customer_schema, login_schema, update_customer_schema
from app.extensions import limiter

#I seperate these code blocks for better readability and organization for me. 
#------------------------------------------------------------------------------
from app.utils import token_required


@customer_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):
    try:
        tickets = db.session.query(ServiceTickets).filter_by(customer_id=customer_id).all()

        tickets_list = [
            {
                "id": ticket.id,
                "service_description": ticket.service_description,
                "cost": ticket.cost,
                "vin_number": ticket.vin_number,
                "work_complete": ticket.work_complete,
                "car_submission_date": ticket.car_submission_date.isoformat(),
                "work_start_date": ticket.work_start_date.isoformat() if ticket.work_start_date else None,
                "work_finish_date": ticket.work_finish_date.isoformat() if ticket.work_finish_date else None,
                "inventory_items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "price": item.price,
                        "quantity": item.quantity
                    }
                    for item in ticket.inventory_items
                ]
            }
            for ticket in tickets
        ]
        return jsonify(tickets_list), 200
    except Exception as e:
        print(f"Error retrieving tickets: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@customer_bp.route("/login", methods=["POST"])
def login_customer():
    try:
        login_data = login_schema.load(request.json)
        email = login_data["email"]
        password = login_data["password"]

        customer = db.session.query(Customers).filter_by(email=email).first()
        if not customer or customer.password != password:
            return jsonify({"message": "Invalid email or password"}), 401

        from app.utils import encode_token
        token = encode_token(customer.id)
        
        return jsonify({"message": "Login successful", "token": token}), 200

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

#-----------------------------------------------------------------------------

@customer_bp.route("/", methods=['POST'])
@limiter.limit("15 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_customer = Customers(name=customer_data["name"],
                             phone_number=customer_data["phone_number"],
                             car_brand=customer_data["car_brand"],
                             car_type=customer_data["car_type"],
                             car_mileage=customer_data["car_mileage"],
                             mechanical_issue=customer_data["mechanical_issue"],
                             email=customer_data["email"],
                             password=customer_data["password"])

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"id": new_customer.id,
                   "name": new_customer.name,
                   "phone_number": new_customer.phone_number,
                   "car_brand": new_customer.car_brand,
                   "car_type": new_customer.car_type,
                   "car_mileage": new_customer.car_mileage,
                   "mechanical_issue": new_customer.mechanical_issue,
                   "email": new_customer.email}), 201


@customer_bp.route("/", methods=["GET"])
def get_customers():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 3, type=int)
        
        pagination = db.session.query(Customers).paginate(page=page, per_page=per_page)
        
        customers_list = [{
            "id": customer.id,
            "name": customer.name,
            "phone_number": customer.phone_number,
            "car_brand": customer.car_brand,
            "car_type": customer.car_type,
            "car_mileage": customer.car_mileage,
            "mechanical_issue": customer.mechanical_issue
        } for customer in pagination.items]

        return jsonify({
            "customers": customers_list,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": "Try again!"}), 500


@customer_bp.route("/search", methods=['GET'])
def search_customer():
    name = request.args.get("name", "")
    query = select(Customers).where(Customers.name.like(f"%{name}%"))
    customers = db.session.execute(query).scalars().all()
    customers_list = [{"id": customer.id, 
                       "name": customer.name,
                       "phone_number": customer.phone_number,
                       "car_brand": customer.car_brand,
                       "car_type": customer.car_type,
                       "car_mileage": customer.car_mileage,
                       "mechanical_issue": customer.mechanical_issue} for customer in customers]
    return jsonify(customers_list), 200


@customer_bp.route("/<int:id>", methods=["PUT"])
def update_customer(id):
    try:
        customer = db.session.query(Customers).filter_by(id=id).first()
        if not customer:
            return jsonify({"message": "Customer not found"}), 404

        try:
            update_data = update_customer_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400

        customer.name = update_data.get("name", customer.name)
        customer.email = update_data.get("email", customer.email)

        db.session.commit()

        return jsonify({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email}), 200
    except Exception as e:
        print(f"Error updating customer: {str(e)}")
        return jsonify({"message": "Error occurred while updating customer"}), 500


@customer_bp.route("/<int:id>", methods=['DELETE'])
def delete_customer(id):
    try:
        customer = db.session.query(Customers).filter_by(id=id).first()
        if not customer:
            return jsonify({"message": "Customer not in database!"}), 404

        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": f"Customer with ID {id} has been deleted"}), 200
    except Exception:
        return jsonify({"message": "Error"}), 500