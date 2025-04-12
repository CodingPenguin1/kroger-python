# tests/test_product.py
import unittest

from kroger.product import Product, ProductPrice, ProductStock


class TestProductPrice(unittest.TestCase):
    """Tests for the ProductPrice class."""

    def test_from_dict_with_valid_data(self):
        """Test creating a ProductPrice from a dictionary with valid data."""
        price_dict = {"regular": 10.99, "promo": 8.99}
        price = ProductPrice.from_dict(price_dict)

        self.assertEqual(price.regular, 10.99)
        self.assertEqual(price.promo, 8.99)
        self.assertTrue(price.is_on_sale)

    def test_from_dict_with_string_prices(self):
        """Test handling string prices."""
        price_dict = {"regular": "10.99", "promo": "8.99"}
        price = ProductPrice.from_dict(price_dict)

        self.assertEqual(price.regular, 10.99)
        self.assertEqual(price.promo, 8.99)

    def test_from_dict_without_promo(self):
        """Test creating a ProductPrice without a promo price."""
        price_dict = {"regular": 10.99}
        price = ProductPrice.from_dict(price_dict)

        self.assertEqual(price.regular, 10.99)
        self.assertIsNone(price.promo)
        self.assertFalse(price.is_on_sale)

    def test_display_price_with_promo(self):
        """Test display formatting with a promotion."""
        price = ProductPrice(regular=10.99, promo=8.99)
        self.assertEqual(price.display_price, "$8.99 (Reg: $10.99)")

    def test_display_price_without_promo(self):
        """Test display formatting without a promotion."""
        price = ProductPrice(regular=10.99)
        self.assertEqual(price.display_price, "$10.99")


class TestProductStock(unittest.TestCase):
    """Tests for the ProductStock class."""

    def test_from_dict_available(self):
        """Test creating a ProductStock with available status."""
        stock_dict = {"stockLevel": "AVAILABLE"}
        stock = ProductStock.from_dict(stock_dict)

        self.assertEqual(stock.stock_level, "AVAILABLE")
        self.assertTrue(stock.is_available)
        self.assertEqual(stock.display_status, "In Stock")

    def test_from_dict_unavailable(self):
        """Test creating a ProductStock with unavailable status."""
        stock_dict = {"stockLevel": "OUT_OF_STOCK"}
        stock = ProductStock.from_dict(stock_dict)

        self.assertEqual(stock.stock_level, "OUT_OF_STOCK")
        self.assertFalse(stock.is_available)
        self.assertEqual(stock.display_status, "Out of Stock")

    def test_from_dict_default(self):
        """Test creating a ProductStock with missing data."""
        stock_dict = {}
        stock = ProductStock.from_dict(stock_dict)

        self.assertEqual(stock.stock_level, "UNKNOWN")
        self.assertFalse(stock.is_available)


class TestProduct(unittest.TestCase):
    """Tests for the Product class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a sample product item
        self.product_item = {
            "itemId": "0001",
            "price": {"regular": 10.99, "promo": 8.99},
            "size": "12 oz",
            "stock": {"stockLevel": "AVAILABLE"}
        }

        # Create a sample product
        self.product_dict = {
            "productId": "1234567890",
            "upc": "0000000012345",
            "description": "Test Product",
            "brand": "Test Brand",
            "categories": [{"name": "Category 1"}, {"name": "Category 2"}],
            "items": [self.product_item],
            "images": [
                {
                    "perspectives": [
                        {
                            "sizes": [
                                {"size": "large", "url": "http://example.com/image.jpg"}
                            ]
                        }
                    ]
                }
            ]
        }

        self.product = Product.from_dict(self.product_dict)

    def test_from_dict(self):
        """Test creating a Product from a dictionary."""
        self.assertEqual(self.product.product_id, "1234567890")
        self.assertEqual(self.product.description, "Test Product")
        self.assertEqual(self.product.brand, "Test Brand")
        self.assertEqual(self.product.categories, ["Category 1", "Category 2"])
        self.assertEqual(len(self.product.items), 1)
        self.assertEqual(self.product.upc, "0000000012345")

    def test_primary_item(self):
        """Test getting the primary item."""
        primary = self.product.primary_item
        self.assertIsNotNone(primary)
        self.assertEqual(primary.size, "12 oz")

    def test_price(self):
        """Test getting the price."""
        price = self.product.price
        self.assertIsNotNone(price)
        self.assertEqual(price.regular, 10.99)
        self.assertEqual(price.promo, 8.99)

    def test_is_available(self):
        """Test checking availability."""
        self.assertTrue(self.product.is_available)

    def test_size(self):
        """Test getting the size."""
        self.assertEqual(self.product.size, "12 oz")

    def test_get_image_url(self):
        """Test getting an image URL."""
        self.assertEqual(
            self.product.get_image_url(),
            "http://example.com/image.jpg"
        )


if __name__ == '__main__':
    unittest.main()
