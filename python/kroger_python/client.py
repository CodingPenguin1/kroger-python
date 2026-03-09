import base64
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class KrogerToken:
    """Represents an OAuth access token from Kroger API."""

    access_token: str
    expires_in: int
    token_type: str
    expiry_time: float  # Timestamp when token expires

    @property
    def is_valid(self) -> bool:
        """Check if the token is still valid with a 60-second buffer."""
        return time.time() < (self.expiry_time - 60)


class KrogerClient:
    """Client for interacting with the Kroger API using OAuth2 client credentials flow."""

    BASE_URL = "https://api.kroger.com/v1"
    TOKEN_URL = f"{BASE_URL}/connect/oauth2/token"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Kroger API client.

        Args:
            client_id: The client ID provided by Kroger
            client_secret: The client secret provided by Kroger
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: KrogerToken | None = None

    def _get_authorization_header(self) -> str:
        """
        Create the Basic Authorization header for token requests.

        Returns:
            The Basic authorization header value
        """
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded_credentials}"

    def get_token(self, scopes: list[str]) -> KrogerToken:
        """
        Request an access token from the Kroger API.

        Args:
            scopes: List of API scopes required for the application

        Returns:
            KrogerToken object containing the access token and related information

        Raises:
            requests.RequestException: If the token request fails
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_authorization_header(),
        }

        data = {"grant_type": "client_credentials", "scope": " ".join(scopes)}

        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        current_time = time.time()

        self._token = KrogerToken(
            access_token=token_data["access_token"],
            expires_in=token_data["expires_in"],
            token_type=token_data["token_type"],
            expiry_time=current_time + token_data["expires_in"],
        )

        return self._token

    def ensure_valid_token(self, scopes: list[str]) -> KrogerToken:
        """
        Ensure the client has a valid token, requesting a new one if needed.

        Args:
            scopes: List of API scopes required for the application

        Returns:
            KrogerToken object containing a valid access token
        """
        if self._token is None or not self._token.is_valid:
            return self.get_token(scopes)
        return self._token

    def make_request(
        self,
        method: str,
        endpoint: str,
        scopes: list[str],
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an authenticated request to the Kroger API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without the base URL)
            scopes: List of scopes required for this request
            params: Optional query parameters
            data: Optional form data
            json_data: Optional JSON data

        Returns:
            JSON response from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        token = self.ensure_valid_token(scopes)

        headers = {"Accept": "application/json", "Authorization": f"Bearer {token.access_token}"}

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
        )

        response.raise_for_status()
        return response.json()
