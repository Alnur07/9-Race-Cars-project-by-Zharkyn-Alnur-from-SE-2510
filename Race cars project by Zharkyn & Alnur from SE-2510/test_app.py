# test_app.py
import sys
import os
import unittest

# Force Python to look inside project directory first to avoid stale cache imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from Cars.vehicle import BaseVehicle, RaceCar, StreetCar
from Manager.manage import GarageManager
from utils import validate_record_time, time_to_ms


class TestRaceCarSystem(unittest.TestCase):
    """Comprehensive test suite for Race Car Management System.

    Covers: core OOP, functional programming, data persistence,
    polymorphism, input validation, and statistics.
    """

    def setUp(self):
        """Setup execution block running prior to each isolated test case."""
        self.manager = GarageManager()
        self.manager.data_folder = current_dir
        self.test_db_filename = "garage_database.json"
        self.manager.cars = []  # Explicitly clear inner references before each test run

    # --- 1. Core Structural Modification Test Case (add_car) ---
    def test_add_car(self):
        """Verifies successful registration and attributes mapping inside system memory."""
        car = RaceCar("Porsche", "911 GT3 RS", 2100)
        self.manager.add_car(car)

        self.assertEqual(len(self.manager.cars), 1)
        self.assertEqual(self.manager.cars[0].brand, "Porsche")
        self.assertEqual(self.manager.cars[0].model, "911 GT3 RS")

    # --- 2. Advanced Statistics: Mileage Filter (Lambda) ---
    def test_lambda_filter(self):
        """Test advanced statistics: mileage filter (Lambda)."""
        self.manager.add_car(RaceCar("Ferrari", "F8", 1000))
        self.manager.add_car(RaceCar("Lada", "Priora", 150000))

        high_mileage = self.manager.get_filtered_mileage_cars(50000, operator=">")
        self.assertEqual(len(high_mileage), 1)
        self.assertEqual(high_mileage[0].brand, "Lada")

    # --- 3. Advanced Statistics: Brand Stream (Generator) ---
    def test_brand_generator(self):
        """Test advanced statistics: brand stream (Generator)."""
        self.manager.add_car(RaceCar("Ferrari", "F8", 1000))
        self.manager.add_car(RaceCar("Ferrari", "Roma", 2000))
        self.manager.add_car(RaceCar("Lada", "Granta", 80000))

        gen = list(self.manager.generate_cars_by_brand("Ferrari"))
        self.assertEqual(len(gen), 2)

    # --- 4. Constraints Verification Test Case (Memory Duplicates Protection) ---
    def test_add_car_duplicates(self):
        """Ensure that identical vehicle entities are merged instead of creating duplicates."""
        car1 = RaceCar("Ferrari", "F8", 1200)
        self.manager.add_car(car1)

        # Adding exact same model with new mileage criteria
        car2 = RaceCar("Ferrari", "F8", 3500)
        self.manager.add_car(car2)

        # Verify list size remains exactly 1
        self.assertEqual(len(self.manager.cars), 1)

        # Direct check against the entry present within manager memory array
        self.assertEqual(self.manager.cars[0].mileage, 3500)

    # --- 5. Entity Specific Method Test Case (add_record) ---
    def test_add_record(self):
        """Verify state changes when appending racing historical logs to sub-classes."""
        car = RaceCar("Lada", "Priora", 150000)
        car.add_record("Nurburgring", 2026, "12:34:56")

        self.assertIn("Nurburgring", car.records)
        self.assertIn("2026", car.records["Nurburgring"])
        self.assertEqual(car.records["Nurburgring"]["2026"], "12:34:56")

    # --- 6. Polymorphism & Inheritance Test Case ---
    def test_vehicle_polymorphism(self):
        """Verify correct sub-class object instantiation, inheritance, and polymorphic behaviors."""
        race_car = RaceCar("Ferrari", "SF90", 500)
        street_car = StreetCar("Toyota", "Camry", 20000, p_seats=5)

        self.assertIsInstance(race_car, BaseVehicle)
        self.assertIsInstance(street_car, BaseVehicle)

        self.assertTrue(race_car.display_info().startswith("🏎️ [Race Specs]"))
        self.assertTrue(street_car.display_info().startswith("🚗 [Street Specs]"))

    # --- 7. Utility Validation Logic Test Cases ---
    def test_validate_record_time(self):
        """Verify input validation accuracy using strict regular expression patterns."""
        self.assertTrue(validate_record_time("01:42:35"))
        self.assertTrue(validate_record_time("1:05:00"))
        self.assertFalse(validate_record_time("invalid_string_format"))

    def test_time_to_ms(self):
        """Verify standard string timeline conversion into precise integer milliseconds."""
        self.assertEqual(time_to_ms("01:42:35"), 102035)
        self.assertEqual(time_to_ms("broken:format"), 99999999)

    # --- 8. Data Persistence (JSON save and load) ---
    def test_save_and_load(self):
        """Test saving and loading the unified JSON database."""
        car = RaceCar("Lamborghini", "Huracan", 3000)
        car.add_record("Nurburgring", 2026, "07:04:20")
        self.manager.add_car(car)

        self.manager.save_to_json()

        # Reset inner state matrix and rebuild from file track
        self.manager.cars = []
        self.assertTrue(self.manager.load_from_json())
        self.assertEqual(len(self.manager.cars), 1)
        self.assertEqual(self.manager.cars[0].records["Nurburgring"]["2026"], "07:04:20")

    # --- 9. Set Collection Test ---
    def test_unique_brands_set(self):
        """Verify set collection returns unique brand names."""
        self.manager.add_car(RaceCar("Ferrari", "F8", 1000))
        self.manager.add_car(RaceCar("Ferrari", "Roma", 2000))
        self.manager.add_car(StreetCar("Toyota", "Camry", 5000))

        unique = self.manager.get_unique_brands()
        self.assertEqual(len(unique), 2)
        self.assertIn("Ferrari", unique)
        self.assertIn("Toyota", unique)

    def tearDown(self):
        """Teardown execution block tracking post-test garbage collection routines."""
        filepath = os.path.join(self.manager.data_folder, self.test_db_filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()