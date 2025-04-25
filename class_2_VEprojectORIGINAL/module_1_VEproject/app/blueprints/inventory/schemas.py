from app.models import Inventory
from app.extensions import ma

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

inventory_schema = InventorySchema()
inventory_all_schema = InventorySchema(many=True)