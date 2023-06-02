import unittest
import warnings
from api import app


class MyAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

        warnings.simplefilter("ignore", category=DeprecationWarning)


    def test_hello_world(self):
        response = self.app.get('/', headers={'Authorization': 'Basic bGFycnk6MTIzNDU='})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'<p>Welcome to My Final Drill. My name is Larry John</p>')

    def test_get_guest(self):
        response = self.app.get('/guests', headers={'Authorization': 'Basic bGFycnk6MTIzNDU='})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Larry John" in response.data.decode())

    def test_getguest_byId(self):
        response = self.app.get("/guests/10", headers={'Authorization': 'Basic bGFycnk6MTIzNDU='})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Anthony" in response.data.decode())

    def test_search_guests(self):
        response = self.app.get('/guests/search?firstname=John', headers={'Authorization': 'Basic bGFycnk6MTIzNDU='})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Andonga" in response.data.decode())

    def test_get_booking_ByGuest(self):
        response = self.app.get('/guests/15/booking', headers={'Authorization': 'Basic bGFycnk6MTIzNDU='})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Nick" in response.data.decode())


if __name__ == "__main__":
    unittest.main()
