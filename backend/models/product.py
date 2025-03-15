from datetime import datetime
from backend.app import db

class Product(db.Model):
    """Model for products in the catalog."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Product specifications stored as JSON
    specifications = db.Column(db.JSON)

    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'stock': self.stock,
            'is_active': self.is_active,
            'specifications': self.specifications,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_by_category(category):
        """Get all products in a specific category."""
        return Product.query.filter_by(category=category, is_active=True).all()

    @staticmethod
    def get_active_products():
        """Get all active products."""
        return Product.query.filter_by(is_active=True).all()

    def update_stock(self, quantity):
        """Update product stock."""
        if self.stock + quantity < 0:
            raise ValueError("Cannot reduce stock below 0")
        self.stock += quantity
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<Product {self.id} - {self.name}>'

class ProductCategory(db.Model):
    """Model for product categories."""
    __tablename__ = 'product_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def get_active_categories():
        """Get all active categories."""
        return ProductCategory.query.filter_by(is_active=True).all()

    def __repr__(self):
        return f'<ProductCategory {self.name}>'
