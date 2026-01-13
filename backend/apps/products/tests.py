"""
Comprehensive test suite for Products app.
Tests catalog management, search, variants, and pricing.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Category, Product, ProductImage, ProductVariant, PricingTier, Review
from apps.accounts.models import User


class CategoryTests(TestCase):
    """Tests for Product Category model."""
    
    def test_create_category(self):
        """Test creating a product category."""
        category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags',
            description='Eco-friendly paper bags'
        )
        self.assertEqual(category.name, 'Paper Bags')
        self.assertEqual(str(category), 'Paper Bags')
    
    def test_category_slug_uniqueness(self):
        """Test category slug must be unique."""
        Category.objects.create(name='Bags', slug='bags')
        with self.assertRaises(Exception):
            Category.objects.create(name='Other Bags', slug='bags')


class ProductTests(TestCase):
    """Tests for Product model."""
    
    def setUp(self):
        """Create test category and products."""
        self.category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags'
        )
    
    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            name='Brown Paper Bag',
            slug='brown-paper-bag',
            category=self.category,
            description='100% recyclable',
            price=10.00,
            stock=100
        )
        self.assertEqual(product.name, 'Brown Paper Bag')
        self.assertEqual(product.price, 10.00)
        self.assertEqual(product.stock, 100)
    
    def test_product_sku_generation(self):
        """Test product SKU is generated."""
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=5.00
        )
        self.assertIsNotNone(product.sku)
        self.assertEqual(len(product.sku), 8)
    
    def test_product_slug_uniqueness(self):
        """Test product slug must be unique within category."""
        Product.objects.create(
            name='Product A',
            slug='product-a',
            category=self.category,
            price=10.00
        )
        with self.assertRaises(Exception):
            Product.objects.create(
                name='Product A Duplicate',
                slug='product-a',
                category=self.category,
                price=10.00
            )


class ProductVariantTests(TestCase):
    """Tests for ProductVariant model."""
    
    def setUp(self):
        """Create test product."""
        self.category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags'
        )
        self.product = Product.objects.create(
            name='Paper Bag',
            slug='paper-bag',
            category=self.category,
            price=10.00
        )
    
    def test_create_variant(self):
        """Test creating a product variant."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name='Small',
            sku='VARIANT001',
            price=8.00,
            stock=50
        )
        self.assertEqual(variant.name, 'Small')
        self.assertEqual(variant.price, 8.00)
        self.assertEqual(variant.stock, 50)
    
    def test_variant_price_inheritance(self):
        """Test variant inherits product price if not set."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name='Medium'
        )
        self.assertEqual(variant.price, self.product.price)
    
    def test_low_stock_alert(self):
        """Test identifying low stock items."""
        variant = ProductVariant.objects.create(
            product=self.product,
            name='Large',
            stock=5,
            stock_minimum=10
        )
        self.assertTrue(variant.is_low_stock())


class PricingTierTests(TestCase):
    """Tests for B2B pricing tiers."""
    
    def setUp(self):
        """Create test product."""
        self.category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags'
        )
        self.product = Product.objects.create(
            name='Paper Bag',
            slug='paper-bag',
            category=self.category,
            price=10.00
        )
    
    def test_create_pricing_tier(self):
        """Test creating a B2B pricing tier."""
        tier = PricingTier.objects.create(
            product=self.product,
            quantity_min=100,
            quantity_max=500,
            price=8.00
        )
        self.assertEqual(tier.quantity_min, 100)
        self.assertEqual(tier.price, 8.00)
    
    def test_tiered_pricing(self):
        """Test product returns correct tier price."""
        PricingTier.objects.create(
            product=self.product,
            quantity_min=1,
            quantity_max=50,
            price=10.00
        )
        PricingTier.objects.create(
            product=self.product,
            quantity_min=51,
            quantity_max=100,
            price=9.00
        )
        
        tier_1 = self.product.get_price_for_quantity(25)
        tier_2 = self.product.get_price_for_quantity(75)
        
        self.assertEqual(tier_1, 10.00)
        self.assertEqual(tier_2, 9.00)


class ProductSearchTests(APITestCase):
    """Tests for product search functionality."""
    
    def setUp(self):
        """Create test data."""
        self.category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags'
        )
        self.product1 = Product.objects.create(
            name='Brown Paper Bag',
            slug='brown-paper-bag',
            category=self.category,
            description='Durable eco-friendly brown bags',
            price=10.00
        )
        self.product2 = Product.objects.create(
            name='White Paper Bag',
            slug='white-paper-bag',
            category=self.category,
            description='Clean white bags for retail',
            price=12.00
        )
        self.client = APIClient()
    
    def test_search_by_name(self):
        """Test searching products by name."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Brown'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Brown Paper Bag')
    
    def test_search_by_description(self):
        """Test searching products by description."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'eco-friendly'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_filter_by_category(self):
        """Test filtering products by category."""
        url = reverse('product-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_price_range(self):
        """Test filtering products by price range."""
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': 10, 'max_price': 11})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p['price'] == 10.00 for p in response.data['results']))


class ReviewTests(TestCase):
    """Tests for product reviews."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(
            email='reviewer@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Paper Bags',
            slug='paper-bags'
        )
        self.product = Product.objects.create(
            name='Paper Bag',
            slug='paper-bag',
            category=self.category,
            price=10.00
        )
    
    def test_create_review(self):
        """Test creating a product review."""
        review = Review.objects.create(
            product=self.product,
            customer=self.user,
            rating=5,
            title='Excellent Quality',
            comment='Great bags, very durable'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'Excellent Quality')
    
    def test_review_validation(self):
        """Test review rating is between 1 and 5."""
        with self.assertRaises(Exception):
            Review.objects.create(
                product=self.product,
                customer=self.user,
                rating=10
            )
    
    def test_average_rating(self):
        """Test calculating product average rating."""
        Review.objects.create(
            product=self.product,
            customer=self.user,
            rating=5
        )
        Review.objects.create(
            product=self.product,
            customer=User.objects.create_user(
                email='reviewer2@example.com',
                password='testpass123'
            ),
            rating=4
        )
        
        avg = self.product.get_average_rating()
        self.assertEqual(avg, 4.5)
