import unittest
from app import create_app, db


class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.client.post('/mechanics/', json={
            "mechanic_name": "Diego López",
            "email": "diego.lopez@tallereslopez.es",
            "address": "Calle Real, 45, Madrid, España",
            "phone_number": "+34954321678",
            "salary": 35000})

        # Create a customer for authentication and testing
        customer_response = self.client.post('/customers/', json={
            "name": "Basilia Millian",
            "phone_number": "+34305975931",
            "car_brand": "SEAT",
            "car_type": "Coupe",
            "car_mileage": 32000,
            "mechanical_issue": "Engine gets overheated",
            "email": "GranadaEspana@gmail.es",
            "password": "iberico"})
        
        self.customer_id = customer_response.get_json()["id"]
        self.token = self.get_auth_token()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def get_auth_token(self):
        response = self.client.post('/customers/login', json={
            "email": "GranadaEspana@gmail.es",
            "password": "iberico"})
        return response.get_json().get("token")

    def test_create_customer(self):
        payload = {
            "name": "Juan Fernández",
            "phone_number": "+34987654321",
            "car_brand": "Audi",
            "car_type": "Sedán",
            "car_mileage": 28000,
            "mechanical_issue": "El motor tiene dificultad para encender",
            "email": "juan.fernandez@gmail.es",
            "password": "autoJuan12"
        }
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_customer_negative(self):
        payload = {"name": "Juan Fernández"}
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_get_customers(self):
        response = self.client.get('/customers?page=1&per_page=3')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("customers", data)
        self.assertLessEqual(len(data["customers"]), 3)

    def test_search_customer(self):
        response = self.client.get('/customers/search?name=Basilia')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["name"], "Basilia Millian")

    def test_update_customer(self):
        response = self.client.put(f'/customers/{self.customer_id}', json={
            "name": "Basilia Carmen Millian",
            "phone_number": "+34987654321",
            "email": "GranadaEspana@gmail.es",
            "password": "iberico"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["phone_number"], "+34987654321")

    def test_update_customer_negative(self):
        response = self.client.put('/customers/9999', json={
            "name": "Invalid Customer",
            "phone_number": "123-123-1234"})
        self.assertEqual(response.status_code, 404)

    def test_delete_customer(self):
        response = self.client.post('/customers/', json={
            "name": "Juan Fernández",
            "phone_number": "+34987654321",
            "car_brand": "Audi",
            "car_type": "Sedán",
            "car_mileage": 28000,
            "mechanical_issue": "El motor tiene dificultad para encender",
            "email": "juan.fernandez@gmail.com",
            "password": "autoJuan12"})
        customer_id = response.get_json()["id"]

        response = self.client.delete(f'/customers/{customer_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_customer_negative(self):
        response = self.client.delete('/customers/9999')
        self.assertEqual(response.status_code, 404)

    def test_my_tickets_with_authentication(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        inventory_response_1 = self.client.post('/inventory/', json={
            "name": "Brake Pads",
            "price": 50.0,
            "quantity": 20})
        inventory_id_1 = inventory_response_1.get_json()["id"]

        inventory_response_2 = self.client.post('/inventory/', json={
            "name": "Oil Filter",
            "price": 30.0,
            "quantity": 15})
        inventory_id_2 = inventory_response_2.get_json()["id"]

        ticket_response = self.client.post('/service_tickets/', json={
            "service_description": "Cambio de aceite",
            "cost": 250.0,
            "vin_number": "1HGCM82633A654321",
            "work_complete": False,
            "car_submission_date": "2025-04-21",
            "customer_id": self.customer_id,
            "mechanic_id": 1})
        ticket_id = ticket_response.get_json()["id"]
        self.assertEqual(ticket_response.status_code, 201)

        self.client.post(f'/service_tickets/{ticket_id}/add_part', json={"part_id": inventory_id_1})
        self.client.post(f'/service_tickets/{ticket_id}/add_part', json={"part_id": inventory_id_2})

        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)

        tickets = response.get_json()
        self.assertGreater(len(tickets), 0)
        self.assertGreater(len(tickets[0]["inventory_items"]), 0)
        self.assertEqual(tickets[0]["inventory_items"][0]["name"], "Brake Pads")
        self.assertEqual(tickets[0]["inventory_items"][1]["name"], "Oil Filter")

    def test_my_tickets_with_invalid_token(self):
        fake_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "invalidsignature"
        )
        headers = {"Authorization": f"Bearer {fake_token}"}

        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid token", response.get_json()["error"])


if __name__ == '__main__':
    unittest.main()