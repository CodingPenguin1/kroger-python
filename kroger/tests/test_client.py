import unittest
from unittest.mock import patch, MagicMock
import time

from kroger.client import KrogerClient


class TestKrogerClient(unittest.TestCase):
    """Tests for the KrogerClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.client = KrogerClient(self.client_id, self.client_secret)

    @patch("kroger.client.requests.post")
    def test_get_token(self, mock_post):
        """Test getting an access token."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 1800,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        # Call the method
        token = self.client.get_token(["product.compact"])

        # Assertions
        self.assertEqual(token.access_token, "test_access_token")
        self.assertEqual(token.token_type, "Bearer")
        self.assertEqual(token.expires_in, 1800)
        self.assertTrue(token.expiry_time > time.time())

        # Check that the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.client.TOKEN_URL)
        self.assertEqual(kwargs["data"]["grant_type"], "client_credentials")
        self.assertEqual(kwargs["data"]["scope"], "product.compact")

    @patch("kroger.client.KrogerClient.ensure_valid_token")
    @patch("kroger.client.requests.request")
    def test_make_request(self, mock_request, mock_ensure_token):
        """Test making an API request."""
        # Mock the token and response
        mock_token = MagicMock()
        mock_token.access_token = "test_access_token"
        mock_ensure_token.return_value = mock_token

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.make_request(
            method="GET",
            endpoint="/some-endpoint",
            scopes=["product.compact"],
            params={"param": "value"},
        )

        # Assertions
        self.assertEqual(result, {"data": "test_data"})

        # Check request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], "https://api.kroger.com/v1/some-endpoint")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_access_token")
        self.assertEqual(kwargs["params"], {"param": "value"})

    @patch("kroger.client.KrogerClient.make_request")
    def test_get_locations(self, mock_make_request):
        """Test getting store locations."""
        # Mock the response
        mock_make_request.return_value = {"data": [{"locationId": "12345"}]}

        # Call the method
        result = self.client.get_locations(
            {"filter.zipCode.near": "12345"}
        )  # Updated parameter key

        # Assertions
        self.assertEqual(result, {"data": [{"locationId": "12345"}]})

        # Check method was called correctly
        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="/locations",
            scopes=["product.compact"],
            params={"filter.zipCode.near": "12345"},  # Updated parameter key
        )


if __name__ == "__main__":
    unittest.main()
