import unittest
import warnings
from api import app


class MyAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

        warnings.simplefilter("ignore", category=DeprecationWarning)

    def test_index_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "<p>Hello, World!</p>")

    def test_getguest(self):
        response = self.app.get("/guests")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Larry John" in response.data.decode())

    def test_getguest_byId(self):
        response = self.app.get("/guests/10")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Anthony" in response.data.decode())


if __name__ == "__main__":
    unittest.main()
