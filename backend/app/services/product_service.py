"""
Product Service
Handles product CRUD and availability checking
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.product import Product, ProductVariant, Category, ProductAttribute
from app.models.reservation import Reservation, ReservationStatus
from app.schemas.product import ProductCreate, ProductUpdate, ProductAvailabilityCheck


class ProductService:
    """Product management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Category Methods
    
    def create_category(self, name: str, description: str = None, parent_id: int = None, image_url: str = None) -> Category:
        """Create a new category"""
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
            image_url=image_url
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    # Product Attribute Methods
    
    def create_attribute(self, name: str, values: List[str]) -> ProductAttribute:
        """Create a new product attribute"""
        attribute = ProductAttribute(name=name, values=values)
        self.db.add(attribute)
        self.db.commit()
        self.db.refresh(attribute)
        return attribute
    
    def get_attributes(self) -> List[ProductAttribute]:
        """Get all product attributes"""
        return self.db.query(ProductAttribute).all()
    
    def update_attribute(self, attribute_id: int, values: List[str]) -> Optional[ProductAttribute]:
        """Update attribute values"""
        attribute = self.db.query(ProductAttribute).filter(ProductAttribute.id == attribute_id).first()
        if attribute:
            attribute.values = values
            self.db.commit()
            self.db.refresh(attribute)
        return attribute
    
    # Product Methods
    
    def create_product(self, vendor_id: int, data: ProductCreate) -> Product:
        """Create a new product"""
        # Generate SKU if not provided
        if not data.sku:
            data.sku = f"PRD-{vendor_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        product = Product(
            vendor_id=vendor_id,
            name=data.name,
            description=data.description,
            sku=data.sku,
            image_url=data.image_url,
            gallery_images=data.gallery_images,
            cost_price=data.cost_price,
            sales_price=data.sales_price,
            rental_price_hourly=data.rental_price_hourly,
            rental_price_daily=data.rental_price_daily,
            rental_price_weekly=data.rental_price_weekly,
            rental_price_monthly=data.rental_price_monthly,
            security_deposit=data.security_deposit,
            quantity_on_hand=data.quantity_on_hand,
            category_id=data.category_id,
            brand=data.brand,
            color=data.color,
            attributes=data.attributes,
            is_rentable=data.is_rentable,
            is_published=data.is_published
        )
        
        self.db.add(product)
        self.db.commit()
        
        # Create variants
        for variant_data in data.variants:
            variant = ProductVariant(
                product_id=product.id,
                name=variant_data.name,
                sku=variant_data.sku or f"{data.sku}-{variant_data.name}",
                attributes=variant_data.attributes,
                rental_price_hourly=variant_data.rental_price_hourly,
                rental_price_daily=variant_data.rental_price_daily,
                rental_price_weekly=variant_data.rental_price_weekly,
                rental_price_monthly=variant_data.rental_price_monthly,
                quantity_on_hand=variant_data.quantity_on_hand
            )
            self.db.add(variant)
        
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_products(
        self,
        vendor_id: Optional[int] = None,
        category_id: Optional[int] = None,
        is_published: Optional[bool] = None,
        is_rentable: Optional[bool] = None,
        search: Optional[str] = None,
        brand: Optional[str] = None,
        color: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get products with filters and pagination"""
        query = self.db.query(Product)
        
        if vendor_id:
            query = query.filter(Product.vendor_id == vendor_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if is_published is not None:
            query = query.filter(Product.is_published == is_published)
        
        if is_rentable is not None:
            query = query.filter(Product.is_rentable == is_rentable)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        
        if brand:
            query = query.filter(Product.brand == brand)
        
        if color:
            query = query.filter(Product.color == color)
        
        if min_price is not None:
            query = query.filter(Product.rental_price_daily >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.rental_price_daily <= max_price)
        
        total = query.count()
        products = query.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "items": products,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    
    def update_product(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = self.get_product(product_id)
        
        if not product:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        product = self.get_product(product_id)
        
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        
        return True
    
    def toggle_publish(self, product_id: int) -> Optional[Product]:
        """Toggle product publish status"""
        product = self.get_product(product_id)
        
        if not product:
            return None
        
        product.is_published = not product.is_published
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    # Availability Methods
    
    def check_availability(
        self,
        product_id: int,
        start_date: datetime,
        end_date: datetime,
        quantity: int = 1,
        variant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check if product is available for the given date range and quantity
        Prevents double-booking by checking existing reservations
        """
        product = self.get_product(product_id)
        
        if not product:
            return {
                "is_available": False,
                "available_quantity": 0,
                "requested_quantity": quantity,
                "message": "Product not found"
            }
        
        # Get total quantity
        if variant_id:
            variant = self.db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
            total_quantity = variant.quantity_on_hand if variant else 0
        else:
            total_quantity = product.quantity_on_hand
        
        # Find overlapping reservations
        overlapping_reservations = self.db.query(Reservation).filter(
            Reservation.product_id == product_id,
            Reservation.status == ReservationStatus.ACTIVE,
            Reservation.start_date < end_date,
            Reservation.end_date > start_date
        )
        
        if variant_id:
            overlapping_reservations = overlapping_reservations.filter(
                Reservation.variant_id == variant_id
            )
        
        reserved_quantity = sum(r.quantity for r in overlapping_reservations.all())
        available_quantity = total_quantity - reserved_quantity
        
        is_available = available_quantity >= quantity
        
        return {
            "product_id": product_id,
            "variant_id": variant_id,
            "is_available": is_available,
            "available_quantity": available_quantity,
            "requested_quantity": quantity,
            "start_date": start_date,
            "end_date": end_date,
            "conflicts": [] if is_available else [{"message": f"Only {available_quantity} available"}]
        }
    
    def get_availability_calendar(
        self,
        product_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get product availability calendar for date range"""
        product = self.get_product(product_id)
        
        if not product:
            return []
        
        # Get all reservations in date range
        reservations = self.db.query(Reservation).filter(
            Reservation.product_id == product_id,
            Reservation.status == ReservationStatus.ACTIVE,
            Reservation.start_date < end_date,
            Reservation.end_date > start_date
        ).all()
        
        calendar_data = []
        for reservation in reservations:
            calendar_data.append({
                "start_date": reservation.start_date.isoformat(),
                "end_date": reservation.end_date.isoformat(),
                "quantity_reserved": reservation.quantity,
                "order_id": reservation.order_id
            })
        
        return calendar_data
