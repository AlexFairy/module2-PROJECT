import unittest
from app import create_app, db

class TestMechanics(unittest.TestCase):
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

    def test_create_mechanic(self):
        payload = {
            "mechanic_name": "Alberto Millian",
            "email": "AlbertoTenico@gmail.es",
            "address": "Calle Gran Vía de Colón, 18010 Granada, Spain",
            "phone_number": "+34 987594321",
            "salary": 35000}
        
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.get_json())

    def test_create_mechanic_negative(self):
        payload = {"mechanic_name": "Alberto Millian"}
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_get_mechanics(self):
        self.client.post('/mechanics/', json={
            "mechanic_name": "Alberto Millian",
            "email": "AlbertoTenico@gmail.es",
            "address": "Calle Gran Vía de Colón, 18010 Granada, Spain",
            "phone_number": "+34 987594321",
            "salary": 35000})
        
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_search_mechanic(self):
        self.client.post('/mechanics/', json={
            "mechanic_name": "Alberto Millian",
            "email": "AlbertoTenico@gmail.es",
            "address": "Calle Gran Vía de Colón, 18010 Granada, Spain",
            "phone_number": "+34 987594321",
            "salary": 35000})
        
        response = self.client.get('/mechanics/search?mechanic_name=Alberto')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["mechanic_name"], "Alberto Millian")

    def test_update_mechanic(self):
        response = self.client.post('/mechanics/', json={
            "mechanic_name": "Alberto Millian",
            "email": "AlbertoTenico@gmail.es",
            "address": "Calle Gran Vía de Colón, 18010 Granada, Spain",
            "phone_number": "+34 987594321",
            "salary": 35000})
        self.assertEqual(response.status_code, 201)

        mechanic_id = self.extract_mechanic_id(response)
        self.assertIsNotNone(mechanic_id, "Mechanic ID should not be None")

        response = self.client.put(f'/mechanics/{mechanic_id}', json={
            "mechanic_name": "Alberto Millian Updated",
            "email": "AlbertoUpdated@gmail.es",
            "address": "Plaza Nueva, 18010 Granada, Spain",
            "phone_number": "+34 987123456",
            "salary": 40000 })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Mechanic is updated!")

    def test_update_mechanic_negative(self):
        response = self.client.put('/mechanics/9999', json={
            "mechanic_name": "Unknown Mechanic",
            "email": "unknown@example.com",
            "address": "Unknown Address",
            "phone_number": "+00 000 000 000",
            "salary": 0})
        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic(self):
        response = self.client.post('/mechanics/', json={
            "mechanic_name": "Alberto Millian",
            "email": "AlbertoTenico@gmail.es",
            "address": "Calle Gran Vía de Colón, 18010 Granada, Spain",
            "phone_number": "+34 987594321",
            "salary": 35000})
        self.assertEqual(response.status_code, 201)

        mechanic_id = self.extract_mechanic_id(response)
        self.assertIsNotNone(mechanic_id, "Mechanic ID should not be None")

        response = self.client.delete(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mechanic with ID", response.get_json()["message"])

    def test_delete_mechanic_negative(self):
        response = self.client.delete('/mechanics/9999')
        self.assertEqual(response.status_code, 404)

    def extract_mechanic_id(self, response):
        data = response.get_json()
        return data.get("id") if isinstance(data, dict) else None


if __name__ == '__main__':
    unittest.main()