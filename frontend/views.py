"""
Frontend views for rendering pages with database content
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q
from apps.products.models import Product, Category
from apps.orders.models import Order


# Constants for pagination and search
PRODUCTS_PER_PAGE = 12


def home_view(request):
    """Homepage with featured products"""
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list_view(request):
    """
    Product listing page with advanced filtering, search, and pagination.
    
    Query Parameters:
        - category: Filter by category slug (supports both main and subcategories)
        - search: Full-text search query
        - sort: Sort order (price-asc, price-desc, name-asc, name-desc, newest)
        - page: Page number for pagination
        - per_page: Items per page (max 48)
    """
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'pricing_tiers')
    
    # Get hierarchical categories (main categories with subcategories)
    main_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True
    ).prefetch_related('subcategories').order_by('order', 'name')

    # Filter by category if provided (works for both main and subcategories)
    category_slug = request.GET.get('category', '')
    selected_category = None
    selected_main_category = None  # Track which main category is expanded
    
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug, is_active=True).first()
        if selected_category:
            if selected_category.parent:
                # It's a subcategory - filter only by this subcategory
                products = products.filter(
                    Q(category=selected_category) | 
                    Q(additional_categories=selected_category)
                ).distinct()
                selected_main_category = selected_category.parent
            else:
                # It's a main category - filter by it AND all its subcategories
                subcategory_ids = list(selected_category.subcategories.filter(is_active=True).values_list('id', flat=True))
                category_ids = [selected_category.id] + subcategory_ids
                products = products.filter(
                    Q(category_id__in=category_ids) | 
                    Q(additional_categories__id__in=category_ids)
                ).distinct()
                selected_main_category = selected_category
    
    # Search - use full-text search for better results
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    sort_option = request.GET.get('sort', 'newest')
    sort_mapping = {
        'price-asc': 'retail_price',
        'price-desc': '-retail_price',
        'name-asc': 'name',
        'name-desc': '-name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_mapping.get(sort_option, '-created_at'))
    
    # Total count before pagination
    total_products = products.count()
    
    # Pagination
    per_page = min(int(request.GET.get('per_page', PRODUCTS_PER_PAGE)), 48)
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Calculate page range for pagination UI
    current_page = products_page.number
    total_pages = paginator.num_pages
    
    # Show max 5 page numbers around current page
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    page_range = range(start_page, end_page + 1)
    
    # Build breadcrumb items
    breadcrumb_items = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Products', 'url': '/products/' if selected_category else None},
    ]
    if selected_category:
        breadcrumb_items.append({'name': selected_category.name, 'url': None})
    
    return render(request, 'product_list.html', {
        'products': products_page,
        'categories': main_categories,  # Hierarchical categories
        'selected_category': category_slug,
        'selected_category_obj': selected_category,
        'selected_main_category': selected_main_category,  # For expanding the right category
        'search_query': search_query,
        'sort_option': sort_option,
        'breadcrumb_items': breadcrumb_items,
        # Pagination context
        'paginator': paginator,
        'page_obj': products_page,
        'page_range': page_range,
        'total_products': total_products,
        'per_page': per_page,
    })


def product_search_ajax(request):
    """
    AJAX endpoint for real-time product search with filtering.
    Returns JSON response for dynamic page updates without reload.
    
    Query Parameters:
        - search: Search query string
        - category: Category slug filter (supports both main and subcategories)
        - sort: Sort order
        - page: Page number
        - per_page: Items per page (max 48)
    """
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'pricing_tiers')
    
    # Apply category filter (supports hierarchical categories)
    category_slug = request.GET.get('category', '')
    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug, is_active=True).first()
        if selected_category:
            if selected_category.parent:
                # It's a subcategory - filter only by this subcategory
                products = products.filter(
                    Q(category=selected_category) | 
                    Q(additional_categories=selected_category)
                ).distinct()
            else:
                # It's a main category - filter by it AND all its subcategories
                subcategory_ids = list(selected_category.subcategories.filter(is_active=True).values_list('id', flat=True))
                category_ids = [selected_category.id] + subcategory_ids
                products = products.filter(
                    Q(category_id__in=category_ids) | 
                    Q(additional_categories__id__in=category_ids)
                ).distinct()
    
    # Apply search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Apply sorting
    sort_option = request.GET.get('sort', 'newest')
    sort_mapping = {
        'price-asc': 'retail_price',
        'price-desc': '-retail_price',
        'name-asc': 'name',
        'name-desc': '-name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_mapping.get(sort_option, '-created_at'))
    
    # Total count
    total_count = products.count()
    
    # Pagination
    per_page = min(int(request.GET.get('per_page', PRODUCTS_PER_PAGE)), 48)
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Serialize products
    products_data = []
    for product in products_page:
        first_image = product.images.first()
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description[:150] if product.description else '',
            'price': str(product.retail_price),
            'sku': product.sku,
            'category': {
                'name': product.category.name if product.category else None,
                'slug': product.category.slug if product.category else None,
            },
            'image_url': first_image.image.url if first_image else None,
            'in_stock': product.stock_qty > 0,
            'stock_qty': product.stock_qty,
            'url': f'/products/{product.id}/',
        })
    
    # Calculate page range
    current_page = products_page.number
    total_pages = paginator.num_pages
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    return JsonResponse({
        'success': True,
        'products': products_data,
        'pagination': {
            'current_page': current_page,
            'total_pages': total_pages,
            'total_count': total_count,
            'per_page': per_page,
            'has_next': products_page.has_next(),
            'has_previous': products_page.has_previous(),
            'page_range': list(range(start_page, end_page + 1)),
        },
        'filters': {
            'search': search_query,
            'category': category_slug,
            'category_name': selected_category.name if selected_category else None,
            'sort': sort_option,
        }
    })


def product_detail_view(request, pk):
    """Product detail page - modern optimized design"""
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants', 'pricing_tiers', 'reviews'),
        pk=pk,
        is_active=True
    )
    
    
    # Get related products from same category (show 6 for carousel)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).prefetch_related('images', 'pricing_tiers')[:6]
    
    # Build breadcrumb items
    breadcrumb_items = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Products', 'url': '/products/'},
    ]
    if product.category:
        breadcrumb_items.append({
            'name': product.category.name, 
            'url': f'/products/?category={product.category.slug}'
        })
    breadcrumb_items.append({'name': product.name, 'url': None})
    
    return render(request, 'product_detail_optimized.html', {
        'product': product,
        'related_products': related_products,
        'breadcrumb_items': breadcrumb_items
    })


def cart_view(request):
    """Redirect cart page to checkout - cart is now integrated into checkout flow"""
    from django.shortcuts import redirect
    return redirect('checkout')


def checkout_view(request):
    """Checkout page with cart validation"""
    # Get cart items from request (future: from database)
    # For now, cart is managed in localStorage on frontend
    return render(request, 'checkout.html')


def account_dashboard_view(request):
    """User account dashboard with real user data"""
    # Pass user data to template (will be available if authenticated)
    context = {
        'user': request.user if request.user.is_authenticated else None
    }
    return render(request, 'account_dashboard_optimized.html', context)


def orders_view(request):
    """Redirect orders to account dashboard with orders tab active"""
    return redirect('/account/?tab=orders')


def order_detail_view(request, order_number):
    """Order detail page for a specific order number."""
    order = get_object_or_404(Order.objects.select_related('shipping_address', 'billing_address', 'customer').prefetch_related('lines', 'notes', 'shipments'), order_number=order_number)
    return render(request, 'order_detail.html', {
        'order': order
    })


def addresses_view(request):
    """Manage addresses page for authenticated users."""
    return render(request, 'addresses.html')
