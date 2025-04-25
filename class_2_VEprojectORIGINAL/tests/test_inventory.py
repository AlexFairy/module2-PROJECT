import unittest
from app import create_app, db

class TestInventory(unittest.TestCase):
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

    def test_create_inventory(self):
        payload = {
            "name": "filtro de aceite",
            "price": 11.39,
            "quantity": 50}
        
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "filtro de aceite")
        self.assertEqual(data["price"], 11.39)
        self.assertEqual(data["quantity"], 50)

    def test_create_inventory_negative(self):
        payload = {"name": "filtro de aceite"}
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_get_inventory(self):
        self.client.post('/inventory/', json={
            "name": "filtro de aceite",
            "price": 11.39,
            "quantity": 50})
        
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_search_inventory(self):
        self.client.post('/inventory/', json={
            "name": "filtro de aceite",
            "price": 11.39,
            "quantity": 50})
        
        response = self.client.get('/inventory/search?name=filtro')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["name"], "filtro de aceite")

    def test_update_inventory(self):
        response = self.client.post('/inventory/', json={
            "name": "filtro de aceite",
            "price": 11.39,
            "quantity": 50})
        self.assertEqual(response.status_code, 201)

        item_id = response.get_json()["id"]
        self.assertIsNotNone(item_id, "Inventory ID should not be None")

        response = self.client.put(f'/inventory/{item_id}', json={
            "name": "filtro sintético de aceite",
            "price": 14.99,
            "quantity": 30})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "filtro sintético de aceite")
        self.assertEqual(data["price"], 14.99)
        self.assertEqual(data["quantity"], 30)

    def test_update_inventory_negative(self):
        response = self.client.put('/inventory/9999', json={
            "name": "filtro sintético de aceite",
            "price": 14.99,
            "quantity": 30})
        self.assertEqual(response.status_code, 404)

    def test_delete_inventory(self):
        response = self.client.post('/inventory/', json={
            "name": "filtro de aceite",
            "price": 11.39,
            "quantity": 50})
        self.assertEqual(response.status_code, 201)

        item_id = response.get_json()["id"]
        self.assertIsNotNone(item_id, "Inventory ID should not be None")

        response = self.client.delete(f'/inventory/{item_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Inventory item with ID", response.get_json()["message"])

    def test_delete_inventory_negative(self):
        response = self.client.delete('/inventory/9999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()