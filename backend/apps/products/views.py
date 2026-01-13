from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "attributes"]
    search_fields = ["name", "description", "long_description", "sku"]
    ordering_fields = ["retail_price", "name", "created_at", "stock_qty"]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

@api_view(['GET'])
def autocomplete_search(request):
    """
    AI-Powered Autocomplete Search API
    Returns products, categories, and intelligent suggestions
    """
    query = request.GET.get('q', '').strip()
    max_results = int(request.GET.get('max', 8))
    
    if not query or len(query) < 2:
        return Response({
            'products': [],
            'categories': [],
            'suggestions': [],
            'total_count': 0
        })
    
    # Search products with relevance scoring
    products_query = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(sku__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    ).select_related('category').prefetch_related('images')
    
    # Count total for "View all" link
    total_count = products_query.count()
    
    # Limit products
    products = products_query[:max_results]
    
    # Serialize products
    products_data = []
    for product in products:
        first_image = product.images.first()
        products_data.append({
            'id': product.id,
            'name': product.name,
            'url': f'/products/{product.id}/',
            'price': str(product.retail_price),
            'category': product.category.name if product.category else None,
            'image_url': first_image.image.url if first_image else None,
            'thumbnail': first_image.image.url if first_image else None,
            'in_stock': product.stock_qty > 0,
            'sku': product.sku
        })
    
    # Search categories
    categories_query = Category.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).annotate(product_count=Count('products'))[:5]
    
    categories_data = []
    for category in categories_query:
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'url': f'/products/?category={category.slug}',
            'product_count': category.product_count
        })
    
    # Generate AI-powered suggestions (simple keyword suggestions)
    suggestions_data = []
    
    # Related keyword suggestions
    if 'box' in query.lower():
        suggestions_data.append({
            'text': 'cardboard boxes',
            'reason': 'Popular packaging'
        })
        suggestions_data.append({
            'text': 'custom boxes',
            'reason': 'Custom solutions'
        })
    elif 'tape' in query.lower():
        suggestions_data.append({
            'text': 'packing tape',
            'reason': 'Most searched'
        })
        suggestions_data.append({
            'text': 'custom tape',
            'reason': 'Branded options'
        })
    elif 'bag' in query.lower():
        suggestions_data.append({
            'text': 'poly bags',
            'reason': 'Popular choice'
        })
        suggestions_data.append({
            'text': 'paper bags',
            'reason': 'Eco-friendly'
        })
    elif 'bubble' in query.lower():
        suggestions_data.append({
            'text': 'bubble wrap',
            'reason': 'Protection material'
        })
        suggestions_data.append({
            'text': 'bubble mailers',
            'reason': 'Shipping solution'
        })
    else:
        # Generic suggestions based on query
        if len(query) > 2:
            suggestions_data.append({
                'text': f'{query} boxes',
                'reason': 'Common search'
            })
            suggestions_data.append({
                'text': f'custom {query}',
                'reason': 'Personalized option'
            })
    
    return Response({
        'products': products_data,
        'categories': categories_data,
        'suggestions': suggestions_data[:4],
        'total_count': total_count
    })


@api_view(['GET'])
def trending_products(request):
    """
    Returns trending/popular products and search terms.
    Used by AI Search to show popular items when search box is focused.
    """
    # Get popular products (could be based on views, orders, or manual curation)
    popular_products = Product.objects.filter(
        is_active=True,
        stock_qty__gt=0
    ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
    
    products_data = []
    for product in popular_products:
        first_image = product.images.first()
        products_data.append({
            'id': product.id,
            'name': product.name,
            'url': f'/products/{product.id}/',
            'price': str(product.retail_price),
            'category': product.category.name if product.category else None,
            'image_url': first_image.image.url if first_image else None,
        })
    
    # Trending search terms (could be from analytics in future)
    trending_terms = [
        {'term': 'paper bags', 'searches': 1250},
        {'term': 'kraft bags', 'searches': 980},
        {'term': 'custom boxes', 'searches': 870},
        {'term': 'eco packaging', 'searches': 750},
        {'term': 'shopping bags', 'searches': 650},
    ]
    
    return Response({
        'trending': trending_terms,
        'popular_products': products_data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_review_eligibility(request, product_id):
    """
    Check if the current user is eligible to review a product.
    User must have purchased the product to leave a review.
    """
    from apps.orders.models import Order, OrderLine
    
    try:
        product = Product.objects.get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return Response({
            'can_review': False,
            'already_reviewed': False,
            'reason': 'login_required'
        })
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(
        product=product,
        user_email=request.user.email
    ).exists()
    
    if existing_review:
        return Response({
            'can_review': False,
            'already_reviewed': True,
            'reason': 'already_reviewed'
        })
    
    # Check if user has purchased this product (delivered orders)
    has_purchased = OrderLine.objects.filter(
        order__customer=request.user,
        order__status__in=['DELIVERED', 'SHIPPED'],  # Allow review for shipped/delivered orders
        product=product
    ).exists()
    
    return Response({
        'can_review': has_purchased,
        'already_reviewed': False,
        'reason': 'eligible' if has_purchased else 'not_purchased'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request, product_id):
    """
    Submit a review for a product.
    Only users who have purchased the product can submit reviews.
    """
    from apps.orders.models import Order, OrderLine
    
    try:
        product = Product.objects.get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user already reviewed
    if Review.objects.filter(product=product, user_email=request.user.email).exists():
        return Response({'error': 'You have already reviewed this product'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has purchased this product
    has_purchased = OrderLine.objects.filter(
        order__customer=request.user,
        order__status__in=['DELIVERED', 'SHIPPED'],
        product=product
    ).exists()
    
    if not has_purchased:
        return Response({'error': 'You must purchase this product before reviewing it'}, status=status.HTTP_403_FORBIDDEN)
    
    # Validate and create review
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
    
    review = Review.objects.create(
        product=product,
        user_email=request.user.email,
        rating=rating,
        comment=comment,
        verified_purchase=True  # Mark as verified since we confirmed purchase
    )
    
    return Response({
        'success': True,
        'review_id': review.id,
        'message': 'Thank you for your review!'
    }, status=status.HTTP_201_CREATED)
