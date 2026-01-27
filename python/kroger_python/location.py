from .client import KrogerClient
from .pydantic.location import KrogerLocation


def search_locations_by_zip(
    client: KrogerClient,
    zip_code: str,
    radius_miles: int = 10,
    limit: int = 20,
):
    """
    Search for store locations by ZIP code.

    Args:
        zip_code: The ZIP code to search near
        radius_miles: Search radius in miles
        limit: Maximum number of results to return
        chain: Optional chain name filter

    Returns:
        List of Location objects
    """

    response = client.make_request(
        method="GET",
        endpoint="/locations",
        scopes=["product.compact"],  # Minimum scope for location data
        params={
            "filter.zipCode.near": zip_code,
            "filter.radiusInMiles": radius_miles,
            "filter.limit": limit,
        },
    )

    locations = []
    for location_json in response["data"]:
        locations.append(KrogerLocation.model_validate(location_json))

    return locations
