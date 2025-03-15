from flask import Blueprint, request, jsonify
from flask_login import login_required
from backend.app import db
from backend.models.product import Product, ProductCategory

product_bp = Blueprint('product', __name__)

@product_bp.route('/', methods=['GET'])
def get_products():
    """Get all active products with optional filtering."""
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.description.ilike(search_term))
        )
    
    products = query.all()
    return jsonify({
        'products': [product.to_dict() for product in products]
    }), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    product = Product.query.get_or_404(product_id)
    
    if not product.is_active:
        return jsonify({
            'error': 'Product not found',
            'message': 'The requested product is not available'
        }), 404
    
    return jsonify(product.to_dict()), 200

@product_bp.route('/', methods=['POST'])
@login_required
def create_product():
    """Create a new product."""
    data = request.get_json()
    
    required_fields = ['name', 'price', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'message': f'Please provide all required fields: {", ".join(required_fields)}'
        }), 400
    
    # Validate category exists
    category = ProductCategory.query.filter_by(name=data['category']).first()
    if not category:
        return jsonify({
            'error': 'Invalid category',
            'message': 'The specified category does not exist'
        }), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        category=data['category'],
        image_url=data.get('image_url'),
        stock=data.get('stock', 0),
        specifications=data.get('specifications', {})
    )
    
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Creation failed',
            'message': str(e)
        }), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Update a specific product."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'category' in data:
        # Validate category exists
        category = ProductCategory.query.filter_by(name=data['category']).first()
        if not category:
            return jsonify({
                'error': 'Invalid category',
                'message': 'The specified category does not exist'
            }), 400
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'stock' in data:
        product.stock = data['stock']
    if 'specifications' in data:
        product.specifications = data['specifications']
    if 'is_active' in data:
        product.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': str(e)
        }), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Delete (deactivate) a specific product."""
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Deletion failed',
            'message': str(e)
        }), 500

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all active product categories."""
    categories = ProductCategory.get_active_categories()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200

@product_bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    """Create a new product category."""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({
            'error': 'Missing required field',
            'message': 'Please provide a category name'
        }), 400
    
    # Check if category already exists
    existing_category = ProductCategory.query.filter_by(name=data['name']).first()
    if existing_category:
        return jsonify({
            'error': 'Category exists',
            'message': 'A category with this name already exists'
        }), 400
    
    category = ProductCategory(
        name=data['name'],
        description=data.get('description'),
        image_url=data.get('image_url')
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Creation failed',
            'message': str(e)
        }), 500
