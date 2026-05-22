# Cars/vehicle.py
from abc import ABC, abstractmethod


class BaseVehicle(ABC):
    """Abstract base class representing a core vehicle entity."""

    def __init__(self, brand: str, model: str, mileage: int):
        """Initialize base vehicle attributes.

        Args:
            brand: Vehicle manufacturer name
            model: Vehicle model name
            mileage: Odometer reading in kilometers
        """
        self.brand = brand
        self.model = model
        self.mileage = mileage

    @abstractmethod
    def display_info(self) -> str:
        """Abstract method to be implemented by sub-classes to enable polymorphism."""
        pass

    def to_dict(self) -> dict:
        """Serialize base attributes common to all vehicles into a dictionary."""
        return {
            "brand": self.brand,
            "model": self.model,
            "mileage": self.mileage
        }


class RaceCar(BaseVehicle):
    """Sub-class representing a high-performance track racing car."""

    def __init__(self, brand: str, model: str, mileage: int):
        """Initialize race car with empty records dictionary.

        Args:
            brand: Vehicle manufacturer name
            model: Vehicle model name
            mileage: Odometer reading in kilometers
        """
        super().__init__(brand, model, mileage)
        # Structure: { "Track_Name": { "Year": "Time" } }
        self.records = {}

    def add_record(self, track: str, year: int, time_str: str):
        """Add or update a lap time record for a specific track and year.

        Args:
            track: Track name (e.g., "Nurburgring", "Monza")
            year: Year of the record
            time_str: Lap time in MM:SS:ms format
        """
        if track not in self.records:
            self.records[track] = {}
        self.records[track][str(year)] = time_str

    def display_info(self) -> str:
        """Polymorphic implementation displaying racing specifications."""
        return f"🏎️ [Race Specs] {self.brand} {self.model} | Mileage: {self.mileage} km | Tracks: {len(self.records)}"

    def to_dict(self) -> dict:
        """Extend base serialization with racing records profile data."""
        data = super().to_dict()
        data["type"] = "RaceCar"
        data["records"] = self.records
        return data


class StreetCar(BaseVehicle):
    """Sub-class representing a standard city passenger vehicle."""

    def __init__(self, brand: str, model: str, mileage: int, p_seats: int = 5):
        """Initialize street car with passenger seat count.

        Args:
            brand: Vehicle manufacturer name
            model: Vehicle model name
            mileage: Odometer reading in kilometers
            p_seats: Number of passenger seats (default: 5)
        """
        super().__init__(brand, model, mileage)
        self.passenger_seats = p_seats  # Unique specific attribute

    def display_info(self) -> str:
        """Polymorphic implementation displaying passenger/street specifications."""
        return f"🚗 [Street Specs] {self.brand} {self.model} | Mileage: {self.mileage} km | Seats: {self.passenger_seats}"

    def to_dict(self) -> dict:
        """Extend base serialization with street car attributes."""
        data = super().to_dict()
        data["type"] = "StreetCar"
        data["passenger_seats"] = self.passenger_seats
        return data