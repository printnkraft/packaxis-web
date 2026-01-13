"""
Script to populate the content management system with sample data.
Creates blog posts, FAQs, and dynamic menu items.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis.settings')
django.setup()

from apps.content.models import (
    MenuItem, BlogCategory, BlogPost, FAQCategory, FAQ, FooterSection
)
from django.contrib.auth import get_user_model

User = get_user_model()


def create_menu_items():
    """Create dynamic menu items"""
    print("Creating menu items...")
    
    menu_items = [
        # Header menu
        {'title': 'About Us', 'url': '/about/', 'location': 'header', 'order': 1},
        {'title': 'Contact', 'url': '/contact/', 'location': 'header', 'order': 2},
        
        # Footer - Main Links
        {'title': 'Custom Packaging', 'url': '/products/?category=custom', 'location': 'footer_main', 'order': 1},
        {'title': 'Bulk Orders', 'url': '/bulk-orders/', 'location': 'footer_main', 'order': 2},
        {'title': 'Sustainability', 'url': '/sustainability/', 'location': 'footer_main', 'order': 3},
        
        # Footer - Support
        {'title': 'Contact Us', 'url': '/contact/', 'location': 'footer_support', 'order': 1},
        {'title': 'Shipping Info', 'url': '/shipping/', 'location': 'footer_support', 'order': 2},
        {'title': 'Returns', 'url': '/returns/', 'location': 'footer_support', 'order': 3},
        {'title': 'Track Order', 'url': '/orders/', 'location': 'footer_support', 'order': 4},
        
        # Footer - Legal
        {'title': 'Privacy Policy', 'url': '/privacy/', 'location': 'footer_legal', 'order': 1},
        {'title': 'Terms of Service', 'url': '/terms/', 'location': 'footer_legal', 'order': 2},
        {'title': 'Refund Policy', 'url': '/refunds/', 'location': 'footer_legal', 'order': 3},
    ]
    
    for item_data in menu_items:
        MenuItem.objects.get_or_create(
            title=item_data['title'],
            location=item_data['location'],
            defaults=item_data
        )
    
    print(f"✓ Created {len(menu_items)} menu items")


def create_blog_content():
    """Create blog categories and posts"""
    print("Creating blog content...")
    
    # Get or create admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@packaxis.ca',
            password='admin123'
        )
    
    # Create categories
    categories_data = [
        {'name': 'Sustainability', 'description': 'Eco-friendly packaging solutions and environmental tips'},
        {'name': 'Industry News', 'description': 'Latest packaging industry updates'},
        {'name': 'Product Guides', 'description': 'How-to guides for choosing the right packaging'},
        {'name': 'Business Tips', 'description': 'Packaging strategies for businesses'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat, _ = BlogCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat.name] = cat
    
    # Create blog posts
    posts_data = [
        {
            'title': 'The Ultimate Guide to Eco-Friendly Packaging Solutions',
            'category': 'Sustainability',
            'excerpt': 'Discover how sustainable packaging can reduce your carbon footprint while enhancing your brand image. Learn about biodegradable materials and recycling best practices.',
            'content': '''
                <h2>Why Choose Eco-Friendly Packaging?</h2>
                <p>In today's environmentally conscious market, choosing eco-friendly packaging is not just a trend—it's a business imperative. Consumers are increasingly making purchasing decisions based on a company's environmental practices.</p>
                
                <h3>Benefits of Sustainable Packaging</h3>
                <ul>
                    <li>Reduced environmental impact</li>
                    <li>Enhanced brand reputation</li>
                    <li>Cost savings through material efficiency</li>
                    <li>Compliance with environmental regulations</li>
                </ul>
                
                <h3>Popular Eco-Friendly Materials</h3>
                <p>Kraft paper, recycled cardboard, biodegradable plastics, and plant-based materials are leading the way in sustainable packaging solutions.</p>
                
                <p>At Packaxis, we offer a wide range of FSC-certified and recyclable packaging options that help your business go green without compromising on quality.</p>
            ''',
            'is_featured': True,
        },
        {
            'title': '5 Ways Custom Branded Bags Boost Your Business',
            'category': 'Business Tips',
            'excerpt': 'Custom packaging is a powerful marketing tool. Learn how branded bags can increase brand awareness, customer loyalty, and sales.',
            'content': '''
                <h2>Transform Your Packaging into a Marketing Tool</h2>
                <p>Custom branded bags are walking advertisements for your business. Every customer who carries your bag becomes a brand ambassador.</p>
                
                <h3>Key Benefits:</h3>
                <ol>
                    <li><strong>Brand Visibility:</strong> Your logo travels with your customers</li>
                    <li><strong>Professional Image:</strong> Premium packaging elevates perceived value</li>
                    <li><strong>Customer Experience:</strong> Quality packaging enhances unboxing moments</li>
                    <li><strong>Word-of-Mouth:</strong> Attractive bags spark conversations</li>
                    <li><strong>Cost-Effective Marketing:</strong> Long-lasting brand exposure</li>
                </ol>
                
                <p>Ready to elevate your brand? Explore our custom printing options today!</p>
            ''',
            'is_featured': True,
        },
        {
            'title': 'How to Choose the Right Paper Bag for Your Restaurant',
            'category': 'Product Guides',
            'excerpt': 'A comprehensive guide to selecting the perfect takeout bags for your food service business. Consider size, material, and branding options.',
            'content': '''
                <h2>Selecting the Perfect Takeout Bag</h2>
                <p>The right takeout bag protects food quality, represents your brand, and provides customer convenience.</p>
                
                <h3>Factors to Consider:</h3>
                <ul>
                    <li><strong>Size:</strong> Match bag size to typical order volumes</li>
                    <li><strong>Strength:</strong> Ensure handles can support food weight</li>
                    <li><strong>Grease Resistance:</strong> Protect against oil and moisture</li>
                    <li><strong>Temperature:</strong> Consider hot or cold food requirements</li>
                    <li><strong>Branding:</strong> Add your logo for brand recognition</li>
                </ul>
                
                <h3>Popular Options:</h3>
                <p>Kraft paper bags with twisted handles, SOS bags for bakeries, and custom printed bags for brand-focused restaurants.</p>
            ''',
        },
        {
            'title': 'New Regulations: What Retailers Need to Know About Plastic Bans',
            'category': 'Industry News',
            'excerpt': 'Stay compliant with new environmental regulations. Learn about plastic bag bans across Canada and alternative solutions.',
            'content': '''
                <h2>Navigating the Plastic Bag Ban</h2>
                <p>Canada is phasing out single-use plastics. Here's what your business needs to know.</p>
                
                <h3>Timeline and Impact:</h3>
                <p>As of December 2023, the manufacture and import of checkout bags, cutlery, and other single-use plastics is prohibited.</p>
                
                <h3>Compliant Alternatives:</h3>
                <ul>
                    <li>Paper bags (recyclable and biodegradable)</li>
                    <li>Reusable fabric totes</li>
                    <li>Compostable plant-based bags</li>
                </ul>
                
                <p>Packaxis offers a full range of compliant packaging solutions to help your business transition smoothly.</p>
            ''',
        },
    ]
    
    for post_data in posts_data:
        category_name = post_data.pop('category')
        post_data['category'] = categories[category_name]
        post_data['author'] = admin_user
        post_data['status'] = 'published'
        post_data['published_at'] = datetime.now() - timedelta(days=7)
        
        BlogPost.objects.get_or_create(
            title=post_data['title'],
            defaults=post_data
        )
    
    print(f"✓ Created {len(categories_data)} categories and {len(posts_data)} blog posts")


def create_faq_content():
    """Create FAQ categories and questions"""
    print("Creating FAQ content...")
    
    # Create categories
    categories_data = [
        {
            'name': 'Ordering & Payment',
            'icon': '🛒',
            'description': 'Questions about placing orders and payment methods',
            'order': 1
        },
        {
            'name': 'Shipping & Delivery',
            'icon': '📦',
            'description': 'Shipping options, times, and tracking',
            'order': 2
        },
        {
            'name': 'Products & Materials',
            'icon': '📋',
            'description': 'Information about our packaging products',
            'order': 3
        },
        {
            'name': 'Custom Printing',
            'icon': '🎨',
            'description': 'Custom branding and printing services',
            'order': 4
        },
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat, _ = FAQCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat.name] = cat
    
    # Create FAQs
    faqs_data = [
        {
            'category': 'Ordering & Payment',
            'question': 'What payment methods do you accept?',
            'answer': '<p>We accept all major credit cards (Visa, MasterCard, American Express), debit cards, PayPal, and bank transfers for large orders. All transactions are secure and encrypted.</p>',
            'is_featured': True,
        },
        {
            'category': 'Ordering & Payment',
            'question': 'Do you offer bulk order discounts?',
            'answer': '<p>Yes! We offer competitive pricing for bulk orders. The more you order, the better the price. Contact our sales team for a custom quote on quantities over 10,000 units.</p>',
        },
        {
            'category': 'Ordering & Payment',
            'question': 'What is your minimum order quantity?',
            'answer': '<p>Our minimum order quantity varies by product. For standard items, the minimum is typically 500-1,000 units. Custom printed products may have higher minimums (usually 2,500-5,000 units).</p>',
        },
        {
            'category': 'Shipping & Delivery',
            'question': 'How long does shipping take?',
            'answer': '<p>Standard shipping typically takes 5-7 business days across Canada. Express shipping (2-3 business days) is available. Custom printed orders require an additional 7-10 business days for production.</p>',
            'is_featured': True,
        },
        {
            'category': 'Shipping & Delivery',
            'question': 'Do you ship internationally?',
            'answer': '<p>Currently, we primarily serve Canadian customers. For international orders, please contact our sales team to discuss shipping options and costs.</p>',
        },
        {
            'category': 'Shipping & Delivery',
            'question': 'Can I track my order?',
            'answer': '<p>Yes! Once your order ships, you\'ll receive a tracking number via email. You can also track your order status in your account dashboard.</p>',
            'is_featured': True,
        },
        {
            'category': 'Products & Materials',
            'question': 'Are your products eco-friendly?',
            'answer': '<p>Absolutely! We prioritize sustainability. Most of our products are made from FSC-certified paper, are recyclable, biodegradable, or made from recycled materials. Look for the eco-friendly badge on product pages.</p>',
            'is_featured': True,
        },
        {
            'category': 'Products & Materials',
            'question': 'What sizes do paper bags come in?',
            'answer': '<p>We offer a wide range of sizes from small (5" x 3" x 8") for jewelry and cosmetics to extra-large (18" x 7" x 19") for clothing and bulk items. View full size charts on each product page.</p>',
        },
        {
            'category': 'Products & Materials',
            'question': 'Are the bags food-safe?',
            'answer': '<p>Yes! Our paper bags designated for food service are food-safe and meet Canadian food safety standards. They are grease-resistant and suitable for takeout, bakeries, and restaurants.</p>',
        },
        {
            'category': 'Custom Printing',
            'question': 'Can I add my logo to the bags?',
            'answer': '<p>Yes! We offer professional custom printing services. You can add your logo, brand colors, and custom designs. Our team will provide a free digital proof for your approval before production.</p>',
            'is_featured': True,
        },
        {
            'category': 'Custom Printing',
            'question': 'What file formats do you accept for custom printing?',
            'answer': '<p>We accept AI, EPS, PDF, and high-resolution PNG or JPG files. Vector formats (AI, EPS) are preferred for best quality. Our design team can also help create artwork if needed.</p>',
        },
        {
            'category': 'Custom Printing',
            'question': 'How long does custom printing take?',
            'answer': '<p>Custom printed orders typically take 7-10 business days for production, plus shipping time. Rush orders may be available—contact us to discuss expedited options.</p>',
        },
    ]
    
    for faq_data in faqs_data:
        category_name = faq_data.pop('category')
        faq_data['category'] = categories[category_name]
        
        FAQ.objects.get_or_create(
            question=faq_data['question'],
            defaults=faq_data
        )
    
    print(f"✓ Created {len(categories_data)} FAQ categories and {len(faqs_data)} FAQs")


def main():
    print("=" * 60)
    print("Populating Content Management System")
    print("=" * 60)
    
    create_menu_items()
    create_blog_content()
    create_faq_content()
    
    print("\n" + "=" * 60)
    print("✓ Content population complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  - Visit /blog/ to see blog posts")
    print("  - Visit /faq/ to see FAQs")
    print("  - Go to /admin/ to manage all content")
    print("  - Header and footer now use dynamic menu items")
    print("\n")


if __name__ == '__main__':
    main()
