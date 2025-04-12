from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, time


@dataclass
class LocationAddress:
    """Represents a location's address."""

    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    zip_code: str
    county: Optional[str]

    @classmethod
    def from_dict(cls, address_dict: Dict[str, Any]) -> "LocationAddress":
        """Create a LocationAddress instance from an address dictionary."""
        return cls(
            address_line1=address_dict.get("addressLine1", ""),
            address_line2=address_dict.get("addressLine2", ""),
            city=address_dict.get("city", ""),
            state=address_dict.get("state", ""),
            zip_code=address_dict.get("zipCode", ""),
            county=address_dict.get("county", ""),
        )


@dataclass
class LocationDepartment:
    """Represents a department within a store location."""

    department_id: str
    name: str

    @classmethod
    def from_dict(cls, dept_dict: Dict[str, Any]) -> "LocationDepartment":
        """Create a LocationDepartment instance from a department dictionary."""
        return cls(department_id=dept_dict.get("departmentId", ""), name=dept_dict.get("name", ""))


@dataclass
class DayHours:
    """Represents hours for a specific day."""

    open: Optional[time]
    close: Optional[time]
    open24: bool

    @classmethod
    def from_dict(cls, hours_dict: Dict[str, Any]) -> "DayHours":
        """Create a DayHours instance from a dictionary."""
        open_time = None
        close_time = None

        if "open" in hours_dict:
            try:
                time_str = hours_dict["open"]
                # Format expected: "HH:MM"
                open_time = datetime.strptime(time_str, "%H:%M").time()
            except (ValueError, TypeError):
                pass

        if "close" in hours_dict:
            try:
                time_str = hours_dict["close"]
                close_time = datetime.strptime(time_str, "%H:%M").time()
            except (ValueError, TypeError):
                pass

        return cls(open=open_time, close=close_time, open24=hours_dict.get("open24", False))


@dataclass
class HoursOfOperation:
    """Represents hours of operation for a location."""

    monday: Optional[DayHours]
    tuesday: Optional[DayHours]
    wednesday: Optional[DayHours]
    thursday: Optional[DayHours]
    friday: Optional[DayHours]
    saturday: Optional[DayHours]
    sunday: Optional[DayHours]

    @classmethod
    def from_dict(cls, hours_dict: Dict[str, Any]) -> "HoursOfOperation":
        """Create a HoursOfOperation instance from a dictionary."""
        days = {
            "monday": None,
            "tuesday": None,
            "wednesday": None,
            "thursday": None,
            "friday": None,
            "saturday": None,
            "sunday": None,
        }

        for day in days.keys():
            if day in hours_dict:
                days[day] = DayHours.from_dict(hours_dict[day])

        return cls(**days)


@dataclass
class GeolocationCoordinates:
    """Represents the latitude and longitude coordinates of a location."""

    latitude: float
    longitude: float

    @classmethod
    def from_dict(cls, coord_dict: Dict[str, Any]) -> "GeolocationCoordinates":
        """Create a GeolocationCoordinates instance from a dictionary."""
        # Handle string or numeric values
        lat = coord_dict.get("latitude", 0.0)
        lng = coord_dict.get("longitude", 0.0)

        if isinstance(lat, str):
            try:
                lat = float(lat)
            except (ValueError, TypeError):
                lat = 0.0

        if isinstance(lng, str):
            try:
                lng = float(lng)
            except (ValueError, TypeError):
                lng = 0.0

        return cls(latitude=lat, longitude=lng)


class Location:
    """Represents a Kroger store location."""

    def __init__(
        self,
        location_id: str,
        name: str,
        address: LocationAddress,
        geolocation_coordinates: GeolocationCoordinates,
        chain: str = "",
        phone: str = "",
        departments: List[LocationDepartment] = None,
        hours: Optional[HoursOfOperation] = None,
        distance: Optional[float] = None,
    ):
        """
        Initialize a Location object.

        Args:
            location_id: The unique identifier for the location
            name: The name of the store location
            address: The address of the store location
            geolocation_coordinates: The latitude and longitude of the location
            chain: The store chain (e.g., "KROGER", "FRED_MEYER")
            phone: The phone number of the store
            departments: List of departments at this location
            hours: Hours of operation
            distance: Distance from search point (if applicable)
        """
        self.location_id = location_id
        self.name = name
        self.address = address
        self.geolocation_coordinates = geolocation_coordinates
        self.chain = chain
        self.phone = phone
        self.departments = departments or []
        self.hours = hours
        self.distance = distance

    @classmethod
    def from_dict(cls, location_dict: Dict[str, Any]) -> "Location":
        """Create a Location instance from a location dictionary."""
        # Process address
        address = LocationAddress.from_dict(location_dict.get("address", {}))

        # Process departments
        departments = []
        for dept in location_dict.get("departments", []):
            departments.append(LocationDepartment.from_dict(dept))

        # Process geolocation
        geolocation = GeolocationCoordinates.from_dict(location_dict.get("geolocation", {}))

        # Process hours
        hours = None
        if "hours" in location_dict:
            hours = HoursOfOperation.from_dict(location_dict["hours"])

        return cls(
            location_id=location_dict.get("locationId", ""),
            name=location_dict.get("name", ""),
            address=address,
            geolocation_coordinates=geolocation,
            chain=location_dict.get("chain", ""),
            phone=location_dict.get("phone", ""),
            departments=departments,
            hours=hours,
            distance=location_dict.get("distance", None),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the location to a dictionary."""
        result = {
            "location_id": self.location_id,
            "name": self.name,
            "chain": self.chain,
            "address": {
                "address_line1": self.address.address_line1,
                "city": self.address.city,
                "state": self.address.state,
                "zip_code": self.address.zip_code,
            },
            "phone": self.phone,
            "coordinates": {
                "latitude": self.geolocation_coordinates.latitude,
                "longitude": self.geolocation_coordinates.longitude,
            },
            "departments": [{"name": dept.name} for dept in self.departments],
        }

        if self.address.address_line2:
            result["address"]["address_line2"] = self.address.address_line2

        if self.address.county:
            result["address"]["county"] = self.address.county

        if self.distance is not None:
            result["distance"] = self.distance

        return result

    def __str__(self) -> str:
        """Return a string representation of the location."""
        return f"{self.name} - {self.address.city}, {self.address.state}"

    def display(self) -> str:
        """Format the location information for display."""
        lines = []
        separator = "=" * 50

        lines.append(f"\n{separator}")
        lines.append(f"Store: {self.name}")
        lines.append(f"{separator}")

        lines.append(f"ID: {self.location_id}")
        lines.append(f"Chain: {self.chain}")

        # Address
        lines.append("Address:")
        lines.append(f"  {self.address.address_line1}")
        if self.address.address_line2:
            lines.append(f"  {self.address.address_line2}")
        lines.append(f"  {self.address.city}, {self.address.state} {self.address.zip_code}")

        if self.phone:
            lines.append(f"Phone: {self.phone}")

        if self.distance is not None:
            lines.append(f"Distance: {self.distance:.2f} miles")

        # Departments
        if self.departments:
            lines.append("Departments:")
            for dept in self.departments:
                lines.append(f"  - {dept.name}")

        # Hours
        if self.hours:
            lines.append("Hours:")
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for day in days:
                day_hours = getattr(self.hours, day)
                if day_hours:
                    if day_hours.open24:
                        lines.append(f"  {day.capitalize()}: Open 24 Hours")
                    elif day_hours.open and day_hours.close:
                        open_str = day_hours.open.strftime("%I:%M %p")
                        close_str = day_hours.close.strftime("%I:%M %p")
                        lines.append(f"  {day.capitalize()}: {open_str} - {close_str}")
                    else:
                        lines.append(f"  {day.capitalize()}: Closed")

        lines.append(f"{separator}")

        return "\n".join(lines)


def convert_locations_dict_to_objects(locations_dict: Dict[str, Any]) -> List[Location]:
    """
    Convert a locations API response dictionary to a list of Location objects.

    Args:
        locations_dict: Dictionary from Kroger API response

    Returns:
        List of Location objects
    """
    locations = []

    if "data" in locations_dict:
        for location_data in locations_dict["data"]:
            locations.append(Location.from_dict(location_data))

    return locations
