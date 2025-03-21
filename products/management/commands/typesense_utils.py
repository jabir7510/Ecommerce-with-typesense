# products/typesense_utils.py
import typesense

client = typesense.Client({
    'api_key': 'Ayr2upApcoOux41qCqXcfo3oftt8NmsfjBZNl1ZCtq0WOapv',
    'nodes': [{
        'host': 'localhost',
        'port': 8108,
        'protocol': 'http',
    }],
    'connection_timeout_seconds': 2
})


product_schema = {
    'name': 'products',
    'fields': [
        {'name': 'id', 'type': 'int32'},
        {'name': 'title', 'type': 'string'},
        {'name': 'price', 'type': 'float'},
        {'name': 'description', 'type': 'string'},
        {'name': 'category', 'type': 'string'},
        {'name': 'image', 'type': 'string'},
    ],
    'default_sorting_field': 'price'
}

def initialize_typesense_collection():
    try:
        # Delete existing collection if it exists (optional, for reset)
        client.collections['products'].delete()
    except Exception:
        pass  # Ignore if collection doesn’t exist
    client.collections.create(product_schema)

# Index a single product
def index_product(product):
    document = {
        'id': str(product.id),  
        'title': product.title,
        'price': float(product.price),
        'description': product.description,
        'category': product.category,
        'image': product.image,

    }
    client.collections['products'].documents.upsert(document)


def bulk_index_products():
    from ...models import Product
    products = Product.objects.all()
    for product in products:
        index_product(product)