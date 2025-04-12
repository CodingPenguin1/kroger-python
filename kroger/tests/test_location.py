import unittest
from datetime import time

from kroger.location import (
    Location,
    LocationAddress,
    LocationDepartment,
    DayHours,
    HoursOfOperation,
    GeolocationCoordinates,
    convert_locations_dict_to_objects,
)


class TestLocationAddress(unittest.TestCase):
    """Tests for the LocationAddress class."""

    def test_from_dict_complete(self):
        """Test creating a LocationAddress with complete data."""
        address_dict = {
            "addressLine1": "1234 Main St",
            "addressLine2": "Suite 100",
            "city": "Cincinnati",
            "state": "OH",
            "zipCode": "45202",
            "county": "Hamilton",
        }

        address = LocationAddress.from_dict(address_dict)

        self.assertEqual(address.address_line1, "1234 Main St")
        self.assertEqual(address.address_line2, "Suite 100")
        self.assertEqual(address.city, "Cincinnati")
        self.assertEqual(address.state, "OH")
        self.assertEqual(address.zip_code, "45202")
        self.assertEqual(address.county, "Hamilton")

    def test_from_dict_minimal(self):
        """Test creating a LocationAddress with minimal data."""
        address_dict = {
            "addressLine1": "1234 Main St",
            "city": "Cincinnati",
            "state": "OH",
            "zipCode": "45202",
        }

        address = LocationAddress.from_dict(address_dict)

        self.assertEqual(address.address_line1, "1234 Main St")
        self.assertEqual(address.address_line2, "")
        self.assertEqual(address.city, "Cincinnati")
        self.assertEqual(address.state, "OH")
        self.assertEqual(address.zip_code, "45202")
        self.assertEqual(address.county, "")


class TestLocationDepartment(unittest.TestCase):
    """Tests for the LocationDepartment class."""

    def test_from_dict(self):
        """Test creating a LocationDepartment from a dictionary."""
        dept_dict = {"departmentId": "123", "name": "Pharmacy"}

        dept = LocationDepartment.from_dict(dept_dict)

        self.assertEqual(dept.department_id, "123")
        self.assertEqual(dept.name, "Pharmacy")

    def test_from_dict_empty(self):
        """Test creating a LocationDepartment with empty data."""
        dept_dict = {}

        dept = LocationDepartment.from_dict(dept_dict)

        self.assertEqual(dept.department_id, "")
        self.assertEqual(dept.name, "")


class TestDayHours(unittest.TestCase):
    """Tests for the DayHours class."""

    def test_from_dict_regular_hours(self):
        """Test creating DayHours with regular open/close times."""
        hours_dict = {"open": "08:00", "close": "22:00", "open24": False}

        day_hours = DayHours.from_dict(hours_dict)

        self.assertEqual(day_hours.open, time(8, 0))
        self.assertEqual(day_hours.close, time(22, 0))
        self.assertFalse(day_hours.open24)

    def test_from_dict_24hr(self):
        """Test creating DayHours with 24-hour operations."""
        hours_dict = {"open24": True}

        day_hours = DayHours.from_dict(hours_dict)

        self.assertIsNone(day_hours.open)
        self.assertIsNone(day_hours.close)
        self.assertTrue(day_hours.open24)

    def test_from_dict_invalid_times(self):
        """Test handling invalid time strings."""
        hours_dict = {"open": "invalid", "close": "also invalid", "open24": False}

        day_hours = DayHours.from_dict(hours_dict)

        self.assertIsNone(day_hours.open)
        self.assertIsNone(day_hours.close)
        self.assertFalse(day_hours.open24)


class TestHoursOfOperation(unittest.TestCase):
    """Tests for the HoursOfOperation class."""

    def test_from_dict_full_week(self):
        """Test creating HoursOfOperation with data for all days."""
        hours_dict = {
            "monday": {"open": "08:00", "close": "22:00", "open24": False},
            "tuesday": {"open": "08:00", "close": "22:00", "open24": False},
            "wednesday": {"open": "08:00", "close": "22:00", "open24": False},
            "thursday": {"open": "08:00", "close": "22:00", "open24": False},
            "friday": {"open": "08:00", "close": "23:00", "open24": False},
            "saturday": {"open": "08:00", "close": "23:00", "open24": False},
            "sunday": {"open": "09:00", "close": "21:00", "open24": False},
        }

        hours = HoursOfOperation.from_dict(hours_dict)

        self.assertEqual(hours.monday.open, time(8, 0))
        self.assertEqual(hours.monday.close, time(22, 0))
        self.assertEqual(hours.friday.close, time(23, 0))
        self.assertEqual(hours.sunday.open, time(9, 0))
        self.assertEqual(hours.sunday.close, time(21, 0))

    def test_from_dict_partial(self):
        """Test creating HoursOfOperation with partial data."""
        hours_dict = {
            "monday": {"open": "08:00", "close": "22:00", "open24": False},
            "friday": {"open": "08:00", "close": "23:00", "open24": False},
            "sunday": {"open24": True},
        }

        hours = HoursOfOperation.from_dict(hours_dict)

        self.assertIsNotNone(hours.monday)
        self.assertIsNone(hours.tuesday)
        self.assertIsNone(hours.wednesday)
        self.assertIsNone(hours.thursday)
        self.assertIsNotNone(hours.friday)
        self.assertIsNone(hours.saturday)
        self.assertIsNotNone(hours.sunday)
        self.assertTrue(hours.sunday.open24)


class TestGeolocationCoordinates(unittest.TestCase):
    """Tests for the GeolocationCoordinates class."""

    def test_from_dict_numeric(self):
        """Test creating GeolocationCoordinates with numeric values."""
        coord_dict = {"latitude": 39.1031, "longitude": -84.5120}

        coords = GeolocationCoordinates.from_dict(coord_dict)

        self.assertEqual(coords.latitude, 39.1031)
        self.assertEqual(coords.longitude, -84.5120)

    def test_from_dict_string(self):
        """Test creating GeolocationCoordinates with string values."""
        coord_dict = {"latitude": "39.1031", "longitude": "-84.5120"}

        coords = GeolocationCoordinates.from_dict(coord_dict)

        self.assertEqual(coords.latitude, 39.1031)
        self.assertEqual(coords.longitude, -84.5120)

    def test_from_dict_empty(self):
        """Test creating GeolocationCoordinates with empty data."""
        coord_dict = {}

        coords = GeolocationCoordinates.from_dict(coord_dict)

        self.assertEqual(coords.latitude, 0.0)
        self.assertEqual(coords.longitude, 0.0)


class TestLocation(unittest.TestCase):
    """Tests for the Location class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a sample location data dictionary
        self.location_dict = {
            "locationId": "12345",
            "name": "Test Kroger Store",
            "chain": "KROGER",
            "address": {
                "addressLine1": "1234 Main St",
                "addressLine2": "Suite 100",
                "city": "Cincinnati",
                "state": "OH",
                "zipCode": "45202",
                "county": "Hamilton",
            },
            "geolocation": {
                "latitude": 39.1031,
                "longitude": -84.5120,
                "latLng": "39.1031,-84.5120",
            },
            "phone": "555-123-4567",
            "departments": [
                {"departmentId": "1", "name": "Pharmacy"},
                {"departmentId": "2", "name": "Deli"},
            ],
            "hours": {
                "monday": {"open": "08:00", "close": "22:00", "open24": False},
                "tuesday": {"open": "08:00", "close": "22:00", "open24": False},
                "wednesday": {"open": "08:00", "close": "22:00", "open24": False},
                "thursday": {"open": "08:00", "close": "22:00", "open24": False},
                "friday": {"open": "08:00", "close": "23:00", "open24": False},
                "saturday": {"open": "08:00", "close": "23:00", "open24": False},
                "sunday": {"open": "09:00", "close": "21:00", "open24": False},
            },
            "distance": 2.5,
        }

    def test_from_dict_complete(self):
        """Test creating a Location with complete data."""
        location = Location.from_dict(self.location_dict)

        self.assertEqual(location.location_id, "12345")
        self.assertEqual(location.name, "Test Kroger Store")
        self.assertEqual(location.chain, "KROGER")
        self.assertEqual(location.phone, "555-123-4567")
        self.assertEqual(location.distance, 2.5)

        # Check address
        self.assertEqual(location.address.address_line1, "1234 Main St")
        self.assertEqual(location.address.city, "Cincinnati")

        # Check departments
        self.assertEqual(len(location.departments), 2)
        self.assertEqual(location.departments[0].name, "Pharmacy")
        self.assertEqual(location.departments[1].name, "Deli")

        # Check geolocation
        self.assertEqual(location.geolocation_coordinates.latitude, 39.1031)
        self.assertEqual(location.geolocation_coordinates.longitude, -84.5120)

        # Check hours
        self.assertIsNotNone(location.hours)
        self.assertEqual(location.hours.monday.open, time(8, 0))
        self.assertEqual(location.hours.sunday.close, time(21, 0))

    def test_from_dict_minimal(self):
        """Test creating a Location with minimal data."""
        minimal_dict = {
            "locationId": "12345",
            "name": "Test Kroger Store",
            "address": {
                "addressLine1": "1234 Main St",
                "city": "Cincinnati",
                "state": "OH",
                "zipCode": "45202",
            },
            "geolocation": {"latLng": {"latitude": 39.1031, "longitude": -84.5120}},
        }

        location = Location.from_dict(minimal_dict)

        self.assertEqual(location.location_id, "12345")
        self.assertEqual(location.name, "Test Kroger Store")
        self.assertEqual(location.chain, "")
        self.assertEqual(location.phone, "")
        self.assertIsNone(location.distance)
        self.assertEqual(len(location.departments), 0)
        self.assertIsNone(location.hours)

    def test_to_dict(self):
        """Test converting a Location to a dictionary."""
        location = Location.from_dict(self.location_dict)

        result = location.to_dict()

        self.assertEqual(result["location_id"], "12345")
        self.assertEqual(result["name"], "Test Kroger Store")
        self.assertEqual(result["chain"], "KROGER")
        self.assertEqual(result["address"]["address_line1"], "1234 Main St")
        self.assertEqual(result["address"]["address_line2"], "Suite 100")
        self.assertEqual(result["phone"], "555-123-4567")
        self.assertEqual(result["coordinates"]["latitude"], 39.1031)
        self.assertEqual(result["coordinates"]["longitude"], -84.5120)
        self.assertEqual(result["distance"], 2.5)
        self.assertEqual(len(result["departments"]), 2)
        self.assertEqual(result["departments"][0]["name"], "Pharmacy")

    def test_display(self):
        """Test the display method."""
        location = Location.from_dict(self.location_dict)

        display_str = location.display()

        # Just check that it contains some expected content
        self.assertIn("Test Kroger Store", display_str)
        self.assertIn("1234 Main St", display_str)
        self.assertIn("Cincinnati, OH 45202", display_str)
        self.assertIn("Distance: 2.50 miles", display_str)
        self.assertIn("Pharmacy", display_str)
        self.assertIn("Deli", display_str)

    def test_str(self):
        """Test the string representation."""
        location = Location.from_dict(self.location_dict)

        self.assertEqual(str(location), "Test Kroger Store - Cincinnati, OH")


class TestConvertLocationsDictToObjects(unittest.TestCase):
    """Tests for the convert_locations_dict_to_objects function."""

    def setUp(self):
        """Set up test fixtures."""
        self.location_dict = {
            "locationId": "12345",
            "name": "Test Kroger Store",
            "chain": "KROGER",
            "address": {
                "addressLine1": "1234 Main St",
                "city": "Cincinnati",
                "state": "OH",
                "zipCode": "45202",
            },
            "geolocation": {"latLng": {"latitude": 39.1031, "longitude": -84.5120}},
        }

    def test_convert_multiple_locations(self):
        """Test converting a dictionary with multiple locations."""
        locations_dict = {"data": [self.location_dict, self.location_dict]}

        locations = convert_locations_dict_to_objects(locations_dict)

        self.assertEqual(len(locations), 2)
        self.assertIsInstance(locations[0], Location)
        self.assertEqual(locations[0].location_id, "12345")

    def test_convert_empty_data(self):
        """Test converting a dictionary with empty data."""
        locations_dict = {"data": []}

        locations = convert_locations_dict_to_objects(locations_dict)

        self.assertEqual(len(locations), 0)

    def test_convert_no_data_key(self):
        """Test converting a dictionary without a data key."""
        locations_dict = {"meta": {"count": 0}}

        locations = convert_locations_dict_to_objects(locations_dict)

        self.assertEqual(len(locations), 0)


if __name__ == "__main__":
    unittest.main()
