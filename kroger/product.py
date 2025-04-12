from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ProductPrice:
    """Represents a product's price information."""

    regular: float
    promo: Optional[float] = None

    @classmethod
    def from_dict(cls, price_dict: Dict[str, Any]) -> "ProductPrice":
        """Create a ProductPrice instance from a price dictionary."""
        regular = price_dict.get("regular")
        promo = price_dict.get("promo")

        # Convert string prices to float if needed
        if isinstance(regular, str):
            try:
                regular = float(regular)
            except (ValueError, TypeError):
                regular = 0.0

        if isinstance(promo, str):
            try:
                promo = float(promo)
            except (ValueError, TypeError):
                promo = None

        # Treat $0.00 promo price as None (no promotion)
        if promo == 0:
            promo = None

        return cls(regular=regular, promo=promo)

    @property
    def is_on_sale(self) -> bool:
        """Check if the product is on sale."""
        return self.promo is not None and self.promo < self.regular

    @property
    def display_price(self) -> str:
        """Format the price for display."""
        if self.is_on_sale:
            return f"${self.promo:.2f} (Reg: ${self.regular:.2f})"
        return f"${self.regular:.2f}"

    def __str__(self):
        """String representation of the price."""
        return self.display_price


@dataclass
class ProductStock:
    """Represents a product's stock information."""

    stock_level: str

    @classmethod
    def from_dict(cls, stock_dict: Dict[str, Any]) -> "ProductStock":
        """Create a ProductStock instance from a stock dictionary."""
        return cls(stock_level=stock_dict.get("stockLevel", "UNKNOWN"))

    @property
    def is_available(self) -> bool:
        """Check if the product is available."""
        return self.stock_level == "AVAILABLE"

    @property
    def display_status(self) -> str:
        """Format the stock status for display."""
        return "In Stock" if self.is_available else "Out of Stock"


@dataclass
class ProductItem:
    """Represents a specific item variant of a product."""

    item_id: str
    size: str
    price: ProductPrice
    stock: Optional[ProductStock] = None
    fulfillment: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, item_dict: Dict[str, Any]) -> "ProductItem":
        """Create a ProductItem instance from an item dictionary."""
        price = ProductPrice.from_dict(item_dict.get("price", {}))

        stock = None
        if "stock" in item_dict:
            stock = ProductStock.from_dict(item_dict["stock"])

        return cls(
            item_id=item_dict.get("itemId", ""),
            size=item_dict.get("size", "N/A"),
            price=price,
            stock=stock,
            fulfillment=item_dict.get("fulfillment"),
        )


class Product:
    """Represents a product from the Kroger API."""

    def __init__(
        self,
        product_id: str,
        description: str,
        brand: str = "",
        categories: List[str] = None,
        items: List[ProductItem] = None,
        images: List[Dict[str, Any]] = None,
        upc: str = "",
    ):
        self.product_id = product_id
        self.description = description
        self.brand = brand
        self.categories = categories or []
        self.items = items or []
        self.images = images or []
        self.upc = upc

    @classmethod
    def from_dict(cls, product_dict: Dict[str, Any]) -> "Product":
        """Create a Product instance from a product dictionary."""
        # Process categories
        categories = []
        for category in product_dict.get("categories", []):
            if isinstance(category, dict) and "name" in category:
                categories.append(category["name"])
            elif isinstance(category, str):
                categories.append(category)

        # Process items
        items = [ProductItem.from_dict(item)
                 for item in product_dict.get("items", [])]

        return cls(
            product_id=product_dict.get("productId", ""),
            description=product_dict.get("description", ""),
            brand=product_dict.get("brand", ""),
            categories=categories,
            items=items,
            images=product_dict.get("images", []),
            upc=product_dict.get("upc", ""),
        )

    @property
    def primary_item(self) -> Optional[ProductItem]:
        """Get the primary item variant of the product."""
        return self.items[0] if self.items else None

    @property
    def price(self) -> Optional[ProductPrice]:
        """Get the price of the primary item."""
        return self.primary_item.price if self.primary_item else None

    @property
    def is_available(self) -> bool:
        """Check if the product is available in stock."""
        if not self.primary_item or not self.primary_item.stock:
            return False
        return self.primary_item.stock.is_available

    @property
    def size(self) -> str:
        """Get the size of the primary item."""
        return self.primary_item.size if self.primary_item else "N/A"

    def get_image_url(self, size: str = "large") -> Optional[str]:
        """
        Get the URL of an image of the specified size.

        Args:
            size: Image size ('thumbnail', 'small', 'medium', 'large', 'xlarge')

        Returns:
            URL of the image or None if not found
        """
        for image in self.images:
            perspectives = image.get("perspectives", [])
            for perspective in perspectives:
                sizes = perspective.get("sizes", [])
                for img_size in sizes:
                    if img_size.get("size") == size:
                        return img_size.get("url")
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the product to a dictionary."""
        return {
            "product_id": self.product_id,
            "description": self.description,
            "brand": self.brand,
            "categories": self.categories,
            "price": self.price.display_price if self.price else "N/A",
            "size": self.size,
            "is_available": self.is_available,
            "image_url": self.get_image_url(),
        }

    def __str__(self) -> str:
        """String representation of the product."""
        price_display = self.price.display_price if self.price else "N/A"
        status = "In Stock" if self.is_available else "Out of Stock"
        return f"{self.description} - {self.brand} - {self.size} - {price_display} - {status}"

    def display(self) -> str:
        """Format the product information for display."""
        lines = []
        separator = "=" * 50

        lines.append(f"\n{separator}")
        lines.append(f"Product: {self.description}")
        lines.append(f"{separator}")

        lines.append(f"Brand: {self.brand}")

        if self.price:
            lines.append(f"Price: {self.price.display_price}")

        lines.append(f"Size: {self.size}")

        if self.primary_item and self.primary_item.stock:
            lines.append(
                f"Availability: {self.primary_item.stock.display_status}")

        if self.categories:
            lines.append("Categories:")
            for category in self.categories:
                lines.append(f"  - {category}")

        image_url = self.get_image_url()
        if image_url:
            lines.append(f"Image: {image_url}")

        lines.append(f"{separator}")

        return "\n".join(lines)
