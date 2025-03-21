from django.urls import path
from .views import ProductListSearchView, index, PopulateProducts, SearchSuggestionsView

urlpatterns = [
    path('', index, name='index'),
    path('products/', ProductListSearchView.as_view(), name='product-list'),
    path('populate/', PopulateProducts.as_view(), name='populate-products'),
    path('search_suggestions/', SearchSuggestionsView.as_view(), name='search_suggestions'),
]