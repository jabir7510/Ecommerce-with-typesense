# products/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from .management.commands.typesense_utils import client
from django.shortcuts import render
from django.core.management import call_command
from django.http import JsonResponse
from django.core.cache import cache

def index(request):
    return render(request, 'index.html')

class PopulateProducts(APIView):
    def post(self, request):
        try:
            call_command('fetch_products')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

class ProductListSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None)
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        
        cache_key = f"search_results_{query}_{page}_{per_page}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        if query:
            try:
                search_params = {
                    'q': query,
                    'query_by': 'title,description,category',
                    'per_page': per_page,
                    'page': page,  
                }
                results = client.collections['products'].documents.search(search_params)
                hits = results.get('hits', [])
                product_ids = [int(hit['document']['id']) for hit in hits]
                products = Product.objects.filter(id__in=product_ids)
                serializer = ProductSerializer(products, many=True)
                data = serializer.data
                cache.set(cache_key, data, timeout=300)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Search failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            try:
                products = Product.objects.all()
                serializer = ProductSerializer(products, many=True)
                data = serializer.data
                cache.set(cache_key, data, timeout=300)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Failed to fetch products: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
class SearchSuggestionsView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response([], status=status.HTTP_200_OK)
        
        cache_key = f"suggestions_{query}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        try:
            search_params = {
                'q': query,
                'query_by': 'title,category',  # Focus on title and category for suggestions
                'per_page': 5,  # Limit to 5 suggestions
            }
            results = client.collections['products'].documents.search(search_params)
            hits = results.get('hits', [])
            suggestions = [hit['document']['title'] for hit in hits]
            cache.set(cache_key, suggestions, timeout=300)
            return Response(suggestions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Suggestion failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )