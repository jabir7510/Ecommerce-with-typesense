# products/management/commands/fetch_products.py
from django.core.management.base import BaseCommand
import requests
from products.models import Product
from products.management.commands.typesense_utils import index_product, initialize_typesense_collection

class Command(BaseCommand):
    help = 'Fetch products from Fake Store API and index in Typesense'

    def handle(self, *args, **options):
        initialize_typesense_collection()

        # Fetch products from the new API endpoint with all 150 products
        response = requests.get('https://fakestoreapi.in/api/products?limit=150')
        if response.status_code == 200:
            products_data = response.json()


    

            for prod in products_data['products']:

                product, _ = Product.objects.update_or_create(
                    id=prod['id'],
                    defaults={
                        'title': prod['title'],
                        'price': prod['price'],
                        'description': prod['description'],
                        'category': prod['category'],
                        'image': prod['image'],

                    }
                )
                # Index the product in Typesense
                index_product(product)
            self.stdout.write(self.style.SUCCESS('Products fetched and indexed successfully'))
        else:
            self.stdout.write(self.style.ERROR('Unexpected response format: "products" key not found'))
