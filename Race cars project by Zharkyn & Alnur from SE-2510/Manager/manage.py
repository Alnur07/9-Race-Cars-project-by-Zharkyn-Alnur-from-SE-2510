# Manager/manage.py
from Cars.vehicle import RaceCar, StreetCar
import json
import csv
import os
from utils import log_action

# Tuple of available tracks (immutable collection requirement)
AVAILABLE_TRACKS = ("Nurburgring", "Monza")


class GarageManager:
    """Manager class that handles vehicle collection, persistence, and filtering operations."""

    def __init__(self, data_folder="data"):
        """Initialize manager with empty car list and ensure data folder exists.

        Args:
            data_folder: Path to directory for JSON database storage
        """
        self.cars = []
        self.data_folder = data_folder
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    @log_action
    def add_car(self, car_object):
        """Add a vehicle to the collection, preventing duplicates by brand+model.

        If duplicate exists, updates mileage and merges records instead of creating new entry.

        Args:
            car_object: Instance of RaceCar or StreetCar to add

        Returns:
            True on success
        """
        for existing_car in self.cars:
            if (existing_car.brand.lower() == car_object.brand.lower() and
                existing_car.model.lower() == car_object.model.lower()):
                # Update mileage and merge records for duplicate
                existing_car.mileage = car_object.mileage
                if hasattr(existing_car, 'records') and hasattr(car_object, 'records'):
                    existing_car.records.update(car_object.records)
                return True
        self.cars.append(car_object)
        return True

    @log_action
    def save_to_json(self):
        """Serialize entire polymorphic car list to unified JSON database."""
        filename = os.path.join(self.data_folder, "garage_database.json")
        final_data = [car.to_dict() for car in self.cars]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)

    @log_action
    def load_from_json(self):
        """Load database from JSON file with automatic subclass type restoration.

        Returns:
            True on successful load, False if file missing or corrupt
        """
        filename = os.path.join(self.data_folder, "garage_database.json")
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cars = []
                    for item in data:
                        car_type = item.get("type", "RaceCar")
                        if car_type == "StreetCar":
                            car = StreetCar(
                                item['brand'],
                                item['model'],
                                item['mileage'],
                                item.get('passenger_seats', 5)
                            )
                        else:
                            car = RaceCar(item['brand'], item['model'], item['mileage'])
                            if 'records' in item:
                                car.records = item['records']
                        self.cars.append(car)
                return True
            except (json.JSONDecodeError, KeyError):
                return False
        return False

    def export_records_to_csv(self, track_name, filename=None):
        """Export track leaderboard to CSV file for external analysis.

        Demonstrates CSV module usage for data persistence requirement.

        Args:
            track_name: Track to export records for
            filename: Output CSV path (default: data/{track}_leaderboard.csv)

        Returns:
            Path to created CSV file
        """
        if filename is None:
            filename = os.path.join(self.data_folder, f"{track_name.lower()}_leaderboard.csv")

        # Collect all records for this track
        records = []
        for car in self.cars:
            if isinstance(car, RaceCar) and track_name in car.records:
                for year, time_str in car.records[track_name].items():
                    records.append({
                        'brand': car.brand,
                        'model': car.model,
                        'year': year,
                        'time': time_str
                    })

        # Write CSV with headers
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'model', 'year', 'time'])
            writer.writeheader()
            writer.writerows(records)

        return filename

    def import_records_from_csv(self, filename, track_name):
        """Import track records from CSV file into existing RaceCars.

        Args:
            filename: Path to CSV file with columns: brand,model,year,time
            track_name: Track to associate imported records with

        Returns:
            Number of records imported
        """
        imported = 0
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Find matching car in collection
                for car in self.cars:
                    if (isinstance(car, RaceCar) and
                        car.brand == row['brand'] and
                        car.model == row['model']):
                        car.add_record(track_name, int(row['year']), row['time'])
                        imported += 1
                        break
        return imported

    def get_filtered_mileage_cars(self, threshold_km, operator='>'):
        """Filter cars by mileage using lambda expressions and built-in filter().

        Args:
            threshold_km: Mileage threshold value
            operator: '>' for above threshold, '<' for below

        Returns:
            List of cars matching the filter criteria
        """
        if operator == '<':
            return list(filter(lambda c: c.mileage < threshold_km, self.cars))
        else:
            return list(filter(lambda c: c.mileage > threshold_km, self.cars))

    def generate_cars_by_brand(self, target_brand):
        """Custom generator for memory-efficient streaming of cars by brand.

        Args:
            target_brand: Brand name to filter by (case-insensitive)

        Yields:
            Car objects matching the target brand
        """
        for car in self.cars:
            if car.brand.lower() == target_brand.lower():
                yield car

    def get_all_car_models_uppercase(self):
        """Transform all model names to uppercase using map().

        Returns:
            List of uppercase model strings
        """
        return list(map(lambda c: c.model.upper(), self.cars))

    def get_unique_brands(self):
        """Get set of unique brands in the collection.

        Returns:
            Set of unique brand names (demonstrates set usage)
        """
        return set(car.brand for car in self.cars)