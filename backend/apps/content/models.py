from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()


class MenuItem(models.Model):
    """Dynamic menu items for header/footer navigation"""
    LOCATION_CHOICES = [
        ('header', 'Header Menu'),
        ('footer_main', 'Footer - Main Links'),
        ('footer_support', 'Footer - Support'),
        ('footer_legal', 'Footer - Legal'),
    ]

    title = models.CharField(max_length=100)
    url = models.CharField(max_length=500, help_text="URL path or external link")
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='header')
    order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    open_in_new_tab = models.BooleanField(default=False)
    icon_class = models.CharField(max_length=50, blank=True, help_text="CSS icon class (optional)")

    class Meta:
        ordering = ['location', 'order', 'title']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return f"{self.get_location_display()} - {self.title}"


class BlogCategory(models.Model):
    """Blog post categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Blog posts with rich content"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    excerpt = models.TextField(max_length=300, help_text="Short description for listings")
    content = models.TextField(help_text="Full blog post content (HTML supported)")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Stats
    views_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status', '-published_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description:
            self.meta_description = self.excerpt[:160] if self.excerpt else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content:blog_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class FAQCategory(models.Model):
    """FAQ categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    """Frequently Asked Questions"""
    category = models.ForeignKey(FAQCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question[:50]


class FooterSection(models.Model):
    """Custom footer sections with links"""
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Footer Section"
        verbose_name_plural = "Footer Sections"

    def __str__(self):
        return self.title


class HelpCategory(models.Model):
    """Help Center categories for organizing articles"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of this category")
    icon = models.CharField(max_length=50, default='help', help_text="Material icon name (e.g., 'inventory_2', 'local_shipping')")
    color = models.CharField(max_length=20, default='#0D7B7F', help_text="Accent color for this category")
    order = models.IntegerField(default=0, help_text="Display order (lower = first)")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show on help center homepage")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Help Category"
        verbose_name_plural = "Help Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.meta_title:
            self.meta_title = f"{self.name} - Packaxis Help Center"[:70]
        if not self.meta_description:
            self.meta_description = self.description[:160] if self.description else f"Browse {self.name} help articles and guides at Packaxis."
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('content:help_category', kwargs={'slug': self.slug})

    @property
    def article_count(self):
        return self.articles.filter(is_active=True, status='published').count()


class HelpArticle(models.Model):
    """Help Center articles with rich content"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(HelpCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    excerpt = models.TextField(max_length=300, help_text="Short description for listings and search results")
    content = models.TextField(help_text="Full article content (HTML supported)")

    # Organization
    order = models.IntegerField(default=0, help_text="Display order within category")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_read_time = models.IntegerField(default=3, help_text="Estimated read time in minutes")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show on help center homepage")
    is_popular = models.BooleanField(default=False, help_text="Mark as popular article")

    # Related content
    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='referenced_by')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags for search")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords, comma-separated")

    # Analytics
    views_count = models.IntegerField(default=0)
    helpful_yes = models.IntegerField(default=0, help_text="Number of 'Yes, this was helpful' votes")
    helpful_no = models.IntegerField(default=0, help_text="Number of 'No' votes")

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Author
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='help_articles')

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Help Article"
        verbose_name_plural = "Help Articles"
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'order']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = f"{self.title} - Packaxis Help"[:70]
        if not self.meta_description:
            self.meta_description = self.excerpt[:160] if self.excerpt else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content:help_article', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def mark_helpful(self, is_helpful=True):
        if is_helpful:
            self.helpful_yes += 1
        else:
            self.helpful_no += 1
        self.save(update_fields=['helpful_yes', 'helpful_no'])

    @property
    def helpfulness_ratio(self):
        total = self.helpful_yes + self.helpful_no
        if total == 0:
            return 0
        return round((self.helpful_yes / total) * 100)


class HelpArticleSearch(models.Model):
    """Track search queries in help center for analytics"""
    query = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    session_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Help Search Query"
        verbose_name_plural = "Help Search Queries"

    def __str__(self):
        return f"{self.query} ({self.results_count} results)"
