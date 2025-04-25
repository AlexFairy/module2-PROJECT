import unittest
from app import create_app, db

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_create_service_ticket(self):
        payload = {
            "service_description": "arreglo de motores",
            "cost": 1175,
            "vin_number": "1HGCM82633A654321",
            "work_complete": False,
            "car_submission_date": "2021-12-16",
            "work_start_date": "2021-12-20",
            "work_finish_date": None,
            "customer_id": 1,
            "mechanic_id": 2}
        response = self.client.post('/service_tickets/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())
        self.assertIn("message", response.get_json())

    def test_update_service_ticket(self):
        response = self.client.post('/service_tickets/', json={
            "service_description": "arreglo de motores",
            "cost": 1175,
            "vin_number": "1HGCM82633A654321",
            "work_complete": False,
            "car_submission_date": "2021-12-16",
            "work_start_date": "2021-12-20",
            "work_finish_date": None,
            "customer_id": 1,
            "mechanic_id": 2})
        self.assertEqual(response.status_code, 201)

        ticket_id = response.get_json().get("id")
        self.assertIsNotNone(ticket_id, "Service ticket ID should not be None")

        response = self.client.put(f'/service_tickets/{ticket_id}', json={
            "service_description": "Cambio de aceite",
            "cost": 250.0,
            "vin_number": "1HGCM82633A654321",
            "work_complete": True,
            "car_submission_date": "2021-12-16",
            "work_start_date": "2021-12-20",
            "work_finish_date": "2021-12-27",
            "customer_id": 1,
            "mechanic_id": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Service ticket updated successfully!!!")

    def test_delete_service_ticket(self):
        response = self.client.post('/service_tickets/', json={
            "service_description": "arreglo de motores",
            "cost": 1175,
            "vin_number": "1HGCM82633A654321",
            "work_complete": False,
            "car_submission_date": "2021-12-16",
            "work_start_date": "2021-12-20",
            "work_finish_date": None,
            "customer_id": 1,
            "mechanic_id": 2})
        self.assertEqual(response.status_code, 201)

        ticket_id = response.get_json().get("id")
        self.assertIsNotNone(ticket_id, "Service ticket ID should not be None")

        response = self.client.delete(f'/service_tickets/{ticket_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Service ticket with ID", response.get_json()["message"])

if __name__ == '__main__':
    unittest.main()