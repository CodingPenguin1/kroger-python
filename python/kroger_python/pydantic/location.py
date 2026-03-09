from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# === Shared Base Model ===
class KrogerBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# === Nested Sub-Models ===
class Address(KrogerBaseModel):
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    zip_code: str
    county: str | None = None


class Geolocation(KrogerBaseModel):
    latitude: float
    longitude: float
    lat_lng: str


class DayHours(KrogerBaseModel):
    open: str
    close: str
    open24: bool


class Hours(KrogerBaseModel):
    timezone: str | None = None
    gmt_offset: str | None = None
    open24: bool
    monday: DayHours
    tuesday: DayHours
    wednesday: DayHours
    thursday: DayHours
    friday: DayHours
    saturday: DayHours
    sunday: DayHours


class Department(KrogerBaseModel):
    department_id: str
    name: str
    phone: str | None = None
    hours: Hours | None = None
    address: Address | None = None
    geolocation: Geolocation | None = None
    offsite: bool | None = None


# === Main Location Model ===
class KrogerLocation(KrogerBaseModel):
    location_id: str
    store_number: str
    division_number: str
    chain: str
    name: str
    phone: str
    address: Address
    geolocation: Geolocation
    hours: Hours
    departments: list[Department]


