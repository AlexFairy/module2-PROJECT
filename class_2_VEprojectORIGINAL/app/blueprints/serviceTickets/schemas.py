from app.models import ServiceTickets
from app.extensions import ma
from app.blueprints.inventory.schemas import InventorySchema

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    inventory_items = ma.Nested(InventorySchema, many=True)

    class Meta:
        model = ServiceTickets
    customer_id = ma.Int(required=True)
    mechanic_id = ma.Int(required=True)

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)