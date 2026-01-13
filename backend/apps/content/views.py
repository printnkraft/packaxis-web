from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import BlogPost, BlogCategory, FAQ, FAQCategory


def blog_list(request):
    """Display list of published blog posts"""
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(posts, 9)  # 9 posts per page (3x3 grid)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate page range for pagination
    current_page = page_obj.number
    total_pages = paginator.num_pages
    page_range = range(max(1, current_page - 2), min(total_pages + 1, current_page + 3))

    # Get all categories for filter
    categories = BlogCategory.objects.filter(is_active=True)

    # Get featured posts
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True
    ).select_related('author', 'category')[:3]

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'page_range': page_range,
        'total_posts': paginator.count,
        'categories': categories,
        'featured_posts': featured_posts,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'content/blog_list.html', context)


def blog_search(request):
    """AJAX endpoint for blog search with real-time filtering"""
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)

    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')

    # Filter by category
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Search filter
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(page_number)

    # Calculate page range
    current_page = page_obj.number
    total_pages = paginator.num_pages
    page_range = list(range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)))

    # Build posts data for JSON response
    posts_data = []
    for post in page_obj:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt[:150] + '...' if len(post.excerpt) > 150 else post.excerpt,
            'url': post.get_absolute_url(),
            'featured_image': post.featured_image.url if post.featured_image else None,
            'category': {
                'name': post.category.name if post.category else None,
                'slug': post.category.slug if post.category else None,
            } if post.category else None,
            'author': {
                'name': post.author.get_full_name() or post.author.username if post.author else 'Unknown',
            },
            'published_at': post.published_at.strftime('%b %d, %Y') if post.published_at else None,
            'published_at_iso': post.published_at.isoformat() if post.published_at else None,
        })

    return JsonResponse({
        'success': True,
        'posts': posts_data,
        'search_query': search_query,
        'pagination': {
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_posts': paginator.count,
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'page_range': page_range,
        }
    })


def blog_detail(request, slug):
    """Display single blog post"""
    post = get_object_or_404(
        BlogPost.objects.select_related('author', 'category'),
        slug=slug,
        status='published'
    )

    # Increment view count
    post.increment_views()

    # Get related posts
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id).select_related('author', 'category')[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'content/blog_detail.html', context)


def faq_list(request):
    """Display FAQ page"""
    # Get all categories with their FAQs
    categories = FAQCategory.objects.filter(
        is_active=True
    ).prefetch_related('faqs')

    # Get featured FAQs
    featured_faqs = FAQ.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category')[:5]

    # Search
    search_query = request.GET.get('q')
    if search_query:
        faqs = FAQ.objects.filter(
            is_active=True
        ).filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query)
        ).select_related('category')
    else:
        faqs = None

    context = {
        'categories': categories,
        'featured_faqs': featured_faqs,
        'search_query': search_query,
        'search_results': faqs,
    }
    return render(request, 'content/faq_list.html', context)


def contact_page(request):
    "Display Contact Us page"
    return render(request, 'content/contact.html')


# ============================================
# HELP CENTER VIEWS
# ============================================

def help_center(request):
    """Display Help Center homepage with categories and search"""
    from .models import HelpCategory, HelpArticle, HelpArticleSearch

    # Get all categories
    categories = HelpCategory.objects.filter(
        is_active=True
    ).prefetch_related('articles').order_by('order')

    # Get featured articles
    featured_articles = HelpArticle.objects.filter(
        status='published',
        is_active=True,
        is_featured=True
    ).select_related('category').order_by('-published_at')[:6]

    # Get popular articles
    popular_articles = HelpArticle.objects.filter(
        status='published',
        is_active=True,
        is_popular=True
    ).select_related('category').order_by('-views_count')[:8]

    # Recently updated articles
    recent_articles = HelpArticle.objects.filter(
        status='published',
        is_active=True
    ).select_related('category').order_by('-updated_at')[:5]

    # Total stats
    total_articles = HelpArticle.objects.filter(status='published', is_active=True).count()
    total_categories = categories.count()

    context = {
        'categories': categories,
        'featured_articles': featured_articles,
        'popular_articles': popular_articles,
        'recent_articles': recent_articles,
        'total_articles': total_articles,
        'total_categories': total_categories,
    }
    return render(request, 'content/help_center.html', context)


def help_category(request, slug):
    """Display articles within a specific help category"""
    from .models import HelpCategory, HelpArticle

    category = get_object_or_404(HelpCategory, slug=slug, is_active=True)

    articles = HelpArticle.objects.filter(
        category=category,
        status='published',
        is_active=True
    ).order_by('order', 'title')

    # Get related categories
    related_categories = HelpCategory.objects.filter(
        is_active=True
    ).exclude(id=category.id).order_by('order')[:4]

    context = {
        'category': category,
        'articles': articles,
        'related_categories': related_categories,
    }
    return render(request, 'content/help_category.html', context)


def help_article(request, slug):
    """Display single help article"""
    from .models import HelpArticle

    article = get_object_or_404(
        HelpArticle.objects.select_related('category', 'author'),
        slug=slug,
        status='published',
        is_active=True
    )

    # Increment view count
    article.increment_views()

    # Get related articles
    related = article.related_articles.filter(
        status='published',
        is_active=True
    )[:3]

    # If no manual related articles, get from same category
    if not related.exists() and article.category:
        related = HelpArticle.objects.filter(
            category=article.category,
            status='published',
            is_active=True
        ).exclude(id=article.id).order_by('-views_count')[:3]

    # Get prev/next articles in category
    prev_article = None
    next_article = None
    if article.category:
        prev_article = HelpArticle.objects.filter(
            category=article.category,
            status='published',
            is_active=True,
            order__lt=article.order
        ).order_by('-order').first()

        next_article = HelpArticle.objects.filter(
            category=article.category,
            status='published',
            is_active=True,
            order__gt=article.order
        ).order_by('order').first()

    context = {
        'article': article,
        'related_articles': related,
        'prev_article': prev_article,
        'next_article': next_article,
    }
    return render(request, 'content/help_article.html', context)


def help_search(request):
    """Search help articles (supports both page and AJAX)"""
    from .models import HelpArticle, HelpArticleSearch, HelpCategory

    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')

    articles = HelpArticle.objects.filter(
        status='published',
        is_active=True
    ).select_related('category')

    # Filter by category
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    # Search filter
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        ).distinct()

        # Log search query
        HelpArticleSearch.objects.create(
            query=search_query[:255],
            results_count=articles.count(),
            session_id=request.session.session_key or '',
            ip_address=request.META.get('REMOTE_ADDR')
        )

    # Pagination
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get categories for filter
    categories = HelpCategory.objects.filter(is_active=True).order_by('order')

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        articles_data = []
        for article in page_obj:
            articles_data.append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt[:150] + '...' if article.excerpt and len(article.excerpt) > 150 else (article.excerpt or ''),
                'url': article.get_absolute_url(),
                'category': {
                    'name': article.category.name if article.category else None,
                    'slug': article.category.slug if article.category else None,
                    'icon': article.category.icon if article.category else 'help',
                } if article.category else None,
                'difficulty': article.difficulty,
                'read_time': article.estimated_read_time,
                'views': article.views_count,
            })

        return JsonResponse({
            'success': True,
            'articles': articles_data,
            'results': articles_data,
            'search_query': search_query,
            'pagination': {
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_results': paginator.count,
            }
        })

    context = {
        'articles': page_obj,
        'search_query': search_query,
        'selected_category': category_slug,
        'categories': categories,
        'total_results': paginator.count,
    }
    return render(request, 'content/help_search.html', context)


def help_article_feedback(request, slug):
    """Handle article helpfulness feedback"""
    from .models import HelpArticle

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    article = get_object_or_404(HelpArticle, slug=slug, status='published')

    import json
    try:
        data = json.loads(request.body)
        is_helpful = data.get('helpful', True)
    except (json.JSONDecodeError, KeyError):
        is_helpful = request.POST.get('helpful', 'true').lower() == 'true'

    article.mark_helpful(is_helpful)

    return JsonResponse({
        'success': True,
        'helpful_yes': article.helpful_yes,
        'helpful_no': article.helpful_no,
        'ratio': article.helpfulness_ratio
    })
