from app.models import Customers
from app.extensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=['name', 'phone_number', 'car_brand', 'car_type', 'car_mileage', 'mechanical_issue'])
update_customer_schema = CustomerSchema(only=["name", "phone_number", "email", "password"])