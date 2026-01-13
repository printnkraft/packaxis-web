"""
Management command to seed Help Center with initial content
Run with: python manage.py seed_help_center
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import HelpCategory, HelpArticle


class Command(BaseCommand):
    help = 'Seeds the Help Center with initial categories and articles'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Help Center...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Getting Started',
                'slug': 'getting-started',
                'description': 'Everything you need to begin your journey with Packaxis. Learn the basics of ordering, account setup, and navigation.',
                'icon': 'rocket_launch',
                'color': '#0D7B7F',
                'order': 1,
                'is_featured': True,
            },
            {
                'name': 'Products & Customization',
                'slug': 'products-customization',
                'description': 'Explore our product range, customization options, materials, and design guidelines.',
                'icon': 'inventory_2',
                'color': '#6366F1',
                'order': 2,
                'is_featured': True,
            },
            {
                'name': 'Ordering & Pricing',
                'slug': 'ordering-pricing',
                'description': 'Information about placing orders, pricing structure, quotes, and payment options.',
                'icon': 'shopping_cart',
                'color': '#F59E0B',
                'order': 3,
                'is_featured': True,
            },
            {
                'name': 'Artwork & Design',
                'slug': 'artwork-design',
                'description': 'Guidelines for preparing your artwork, file requirements, and design best practices.',
                'icon': 'palette',
                'color': '#EC4899',
                'order': 4,
                'is_featured': True,
            },
            {
                'name': 'Shipping & Delivery',
                'slug': 'shipping-delivery',
                'description': 'Learn about shipping options, delivery times, tracking, and international orders.',
                'icon': 'local_shipping',
                'color': '#10B981',
                'order': 5,
                'is_featured': True,
            },
            {
                'name': 'Returns & Issues',
                'slug': 'returns-issues',
                'description': 'Our return policy, how to report issues, and quality guarantee information.',
                'icon': 'swap_horiz',
                'color': '#EF4444',
                'order': 6,
                'is_featured': False,
            },
            {
                'name': 'Account & Billing',
                'slug': 'account-billing',
                'description': 'Manage your account, payment methods, invoices, and subscription settings.',
                'icon': 'account_circle',
                'color': '#8B5CF6',
                'order': 7,
                'is_featured': False,
            },
            {
                'name': 'Sustainability',
                'slug': 'sustainability',
                'description': 'Learn about our eco-friendly options, certifications, and environmental commitment.',
                'icon': 'eco',
                'color': '#22C55E',
                'order': 8,
                'is_featured': True,
            },
            {
                'name': 'Business & Enterprise',
                'slug': 'business-enterprise',
                'description': 'Solutions for businesses, enterprise accounts, wholesale pricing, and integrations.',
                'icon': 'business',
                'color': '#3B82F6',
                'order': 9,
                'is_featured': False,
            },
            {
                'name': 'Technical Support',
                'slug': 'technical-support',
                'description': 'Troubleshooting guides, system requirements, and technical FAQs.',
                'icon': 'build',
                'color': '#64748B',
                'order': 10,
                'is_featured': False,
            },
            {
                'name': 'Trust & Safety',
                'slug': 'trust-safety',
                'description': 'Information about security, privacy, data protection, and compliance.',
                'icon': 'verified_user',
                'color': '#0EA5E9',
                'order': 11,
                'is_featured': False,
            },
        ]

        # Create categories
        created_categories = {}
        for cat_data in categories_data:
            category, created = HelpCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            created_categories[cat_data['slug']] = category
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} category: {category.name}')

        # Create sample articles for each category
        articles_data = [
            # Getting Started
            {
                'category': 'getting-started',
                'title': 'Welcome to Packaxis - Your Complete Guide',
                'slug': 'welcome-to-packaxis',
                'excerpt': 'A comprehensive introduction to Packaxis and all the amazing things you can create with our custom packaging solutions.',
                'content': '''<h2>Welcome to Packaxis!</h2>
<p>We're thrilled to have you here. Packaxis is your one-stop destination for premium custom packaging solutions that help your brand stand out.</p>

<h3>What We Offer</h3>
<ul>
    <li><strong>Custom Boxes</strong> - From mailer boxes to rigid gift boxes</li>
    <li><strong>Flexible Packaging</strong> - Pouches, bags, and wraps</li>
    <li><strong>Labels & Stickers</strong> - Custom shapes and finishes</li>
    <li><strong>Tissue Paper & Inserts</strong> - Complete unboxing experience</li>
</ul>

<h3>Getting Started is Easy</h3>
<ol>
    <li>Browse our product catalog</li>
    <li>Select your product and customize</li>
    <li>Upload your artwork or use our design tool</li>
    <li>Review your proof and approve</li>
    <li>We produce and ship to you!</li>
</ol>

<h3>Need Help?</h3>
<p>Our support team is available 24/7 to assist you. Don't hesitate to reach out!</p>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'welcome, introduction, getting started, new customer',
            },
            {
                'category': 'getting-started',
                'title': 'How to Create Your First Order',
                'slug': 'create-first-order',
                'excerpt': 'Step-by-step guide to placing your first custom packaging order with Packaxis.',
                'content': '''<h2>Creating Your First Order</h2>
<p>Follow these simple steps to place your first order with Packaxis.</p>

<h3>Step 1: Choose Your Product</h3>
<p>Browse our catalog and select the packaging type that fits your needs. Use filters to narrow down by material, size, or industry.</p>

<h3>Step 2: Customize Your Product</h3>
<p>Select your dimensions, material, finish, and quantity. Our real-time pricing updates as you customize.</p>

<h3>Step 3: Upload Your Design</h3>
<p>Upload your artwork in PDF, AI, or PSD format. Or use our online design tool to create your design from scratch.</p>

<h3>Step 4: Review & Approve</h3>
<p>We'll send you a digital proof within 24 hours. Review it carefully and approve when you're satisfied.</p>

<h3>Step 5: Production & Delivery</h3>
<p>Once approved, we start production. Standard orders ship within 10-15 business days.</p>

<div class="tip">
<strong>Pro Tip:</strong> Save time by creating an account to save your preferences and reorder easily!
</div>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'first order, ordering, how to order, new customer, tutorial',
            },
            {
                'category': 'getting-started',
                'title': 'Understanding Your Account Dashboard',
                'slug': 'account-dashboard-guide',
                'excerpt': 'Learn how to navigate and use all the features in your Packaxis account dashboard.',
                'content': '''<h2>Your Account Dashboard</h2>
<p>Your dashboard is your command center for all things Packaxis.</p>

<h3>Dashboard Overview</h3>
<p>When you log in, you'll see:</p>
<ul>
    <li><strong>Recent Orders</strong> - Quick view of your latest orders and their status</li>
    <li><strong>Saved Designs</strong> - Access your saved artwork and templates</li>
    <li><strong>Quick Reorder</strong> - Reorder previous products with one click</li>
    <li><strong>Account Balance</strong> - View credits and outstanding invoices</li>
</ul>

<h3>Navigation Menu</h3>
<p>Use the left sidebar to access:</p>
<ul>
    <li>Orders - View all orders and track shipments</li>
    <li>Designs - Manage your saved designs</li>
    <li>Addresses - Save shipping addresses</li>
    <li>Payment Methods - Manage cards and billing</li>
    <li>Settings - Update profile and preferences</li>
</ul>''',
                'difficulty': 'beginner',
                'is_featured': False,
                'is_popular': True,
                'tags': 'dashboard, account, navigation, profile',
            },
            
            # Products & Customization
            {
                'category': 'products-customization',
                'title': 'Complete Guide to Custom Mailer Boxes',
                'slug': 'custom-mailer-boxes-guide',
                'excerpt': 'Everything you need to know about our custom mailer boxes - sizes, materials, finishes, and customization options.',
                'content': '''<h2>Custom Mailer Boxes</h2>
<p>Mailer boxes are perfect for e-commerce shipping and subscription boxes. They offer excellent protection and a premium unboxing experience.</p>

<h3>Available Sizes</h3>
<table>
    <tr><th>Size</th><th>Dimensions (L x W x H)</th><th>Best For</th></tr>
    <tr><td>Small</td><td>6" x 4" x 2"</td><td>Cosmetics, jewelry</td></tr>
    <tr><td>Medium</td><td>10" x 8" x 4"</td><td>Apparel, accessories</td></tr>
    <tr><td>Large</td><td>14" x 10" x 6"</td><td>Multiple items, gifts</td></tr>
    <tr><td>Custom</td><td>Any size</td><td>Specific requirements</td></tr>
</table>

<h3>Material Options</h3>
<ul>
    <li><strong>White Corrugated</strong> - Clean look, great print surface</li>
    <li><strong>Kraft Corrugated</strong> - Natural, eco-friendly appearance</li>
    <li><strong>Recycled Board</strong> - 100% recycled content</li>
</ul>

<h3>Customization Options</h3>
<ul>
    <li>Full-color printing (CMYK)</li>
    <li>Spot UV coating</li>
    <li>Foil stamping</li>
    <li>Embossing/debossing</li>
    <li>Custom inserts</li>
</ul>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'mailer boxes, shipping boxes, custom boxes, e-commerce, packaging',
            },
            {
                'category': 'products-customization',
                'title': 'Choosing the Right Material for Your Packaging',
                'slug': 'choosing-packaging-material',
                'excerpt': 'Compare different packaging materials to find the perfect match for your product and brand.',
                'content': '''<h2>Packaging Materials Guide</h2>
<p>Choosing the right material is crucial for product protection, sustainability, and brand perception.</p>

<h3>Corrugated Cardboard</h3>
<p>Best for: Shipping boxes, mailer boxes</p>
<ul>
    <li>Excellent protection</li>
    <li>Lightweight yet durable</li>
    <li>Recyclable</li>
    <li>Available in various flute types</li>
</ul>

<h3>Rigid Paperboard</h3>
<p>Best for: Luxury packaging, gift boxes</p>
<ul>
    <li>Premium look and feel</li>
    <li>Excellent for high-end products</li>
    <li>Superior print quality</li>
</ul>

<h3>Kraft Paper</h3>
<p>Best for: Eco-conscious brands</p>
<ul>
    <li>Natural, rustic appearance</li>
    <li>100% recyclable</li>
    <li>Great for sustainable messaging</li>
</ul>

<h3>Material Comparison</h3>
<table>
    <tr><th>Material</th><th>Protection</th><th>Print Quality</th><th>Eco-Rating</th><th>Cost</th></tr>
    <tr><td>Corrugated</td><td>⭐⭐⭐⭐⭐</td><td>⭐⭐⭐</td><td>⭐⭐⭐⭐</td><td>$$</td></tr>
    <tr><td>Rigid</td><td>⭐⭐⭐⭐</td><td>⭐⭐⭐⭐⭐</td><td>⭐⭐⭐</td><td>$$$</td></tr>
    <tr><td>Kraft</td><td>⭐⭐⭐</td><td>⭐⭐⭐</td><td>⭐⭐⭐⭐⭐</td><td>$</td></tr>
</table>''',
                'difficulty': 'intermediate',
                'is_featured': False,
                'is_popular': True,
                'tags': 'materials, corrugated, kraft, paperboard, eco-friendly, sustainability',
            },
            
            # Ordering & Pricing
            {
                'category': 'ordering-pricing',
                'title': 'Understanding Our Pricing Structure',
                'slug': 'pricing-structure-explained',
                'excerpt': 'Learn how our pricing works, including volume discounts, setup fees, and factors that affect your quote.',
                'content': '''<h2>How Our Pricing Works</h2>
<p>At Packaxis, we believe in transparent pricing. Here's everything you need to know.</p>

<h3>What Affects Pricing</h3>
<ul>
    <li><strong>Quantity</strong> - Higher quantities = lower per-unit cost</li>
    <li><strong>Size</strong> - Larger boxes use more material</li>
    <li><strong>Material</strong> - Premium materials cost more</li>
    <li><strong>Print Coverage</strong> - Full-color vs. single color</li>
    <li><strong>Finishes</strong> - Special finishes add cost</li>
</ul>

<h3>Volume Discounts</h3>
<table>
    <tr><th>Quantity</th><th>Discount</th></tr>
    <tr><td>100-499</td><td>Base price</td></tr>
    <tr><td>500-999</td><td>10% off</td></tr>
    <tr><td>1,000-4,999</td><td>20% off</td></tr>
    <tr><td>5,000+</td><td>30% off</td></tr>
</table>

<h3>One-Time Setup Fees</h3>
<p>Setup fees cover die creation and plate setup. These are one-time charges that don't apply to reorders.</p>

<h3>Get a Custom Quote</h3>
<p>For quantities over 10,000 or complex projects, contact our sales team for a custom quote.</p>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'pricing, cost, discount, volume, quote',
            },
            {
                'category': 'ordering-pricing',
                'title': 'Payment Methods & Options',
                'slug': 'payment-methods',
                'excerpt': 'Learn about all the payment methods we accept and flexible payment options for your orders.',
                'content': '''<h2>Payment Methods</h2>
<p>We offer multiple secure payment options for your convenience.</p>

<h3>Accepted Payment Methods</h3>
<ul>
    <li>Credit/Debit Cards (Visa, Mastercard, Amex, Discover)</li>
    <li>PayPal</li>
    <li>Bank Transfer (ACH)</li>
    <li>Wire Transfer</li>
    <li>Purchase Orders (approved accounts)</li>
</ul>

<h3>Payment Terms</h3>
<p><strong>Standard Orders:</strong> Full payment required at checkout</p>
<p><strong>Enterprise Accounts:</strong> Net 30 terms available upon approval</p>

<h3>Split Payment</h3>
<p>For large orders, we offer split payment options:</p>
<ul>
    <li>50% deposit at order</li>
    <li>50% before shipping</li>
</ul>

<h3>Security</h3>
<p>All transactions are encrypted with 256-bit SSL. We never store your full card details.</p>''',
                'difficulty': 'beginner',
                'is_featured': False,
                'is_popular': False,
                'tags': 'payment, credit card, paypal, invoice, billing',
            },
            
            # Artwork & Design
            {
                'category': 'artwork-design',
                'title': 'Artwork File Requirements & Guidelines',
                'slug': 'artwork-requirements',
                'excerpt': 'Ensure your artwork files are print-ready with our comprehensive file preparation guidelines.',
                'content': '''<h2>Artwork Requirements</h2>
<p>Following these guidelines ensures your packaging prints perfectly.</p>

<h3>Accepted File Formats</h3>
<ul>
    <li><strong>Adobe Illustrator (.ai)</strong> - Preferred</li>
    <li><strong>PDF</strong> - High resolution, fonts outlined</li>
    <li><strong>Adobe Photoshop (.psd)</strong> - 300 DPI minimum</li>
    <li><strong>PNG/JPEG</strong> - 300 DPI, for simple designs only</li>
</ul>

<h3>Color Mode</h3>
<p>All artwork must be in <strong>CMYK color mode</strong>. RGB colors will be converted and may appear different.</p>

<h3>Resolution</h3>
<ul>
    <li>Minimum: 300 DPI at actual print size</li>
    <li>Recommended: 400 DPI for best results</li>
</ul>

<h3>Bleed & Safe Zone</h3>
<ul>
    <li><strong>Bleed:</strong> Extend artwork 0.125" beyond trim line</li>
    <li><strong>Safe Zone:</strong> Keep important elements 0.125" inside trim</li>
</ul>

<h3>Fonts</h3>
<p>Convert all fonts to outlines/curves to prevent font substitution issues.</p>

<div class="warning">
<strong>Important:</strong> We cannot be responsible for print issues caused by improperly prepared artwork.
</div>''',
                'difficulty': 'intermediate',
                'is_featured': True,
                'is_popular': True,
                'tags': 'artwork, file requirements, resolution, CMYK, bleed, fonts',
            },
            {
                'category': 'artwork-design',
                'title': 'Using the Packaxis Design Tool',
                'slug': 'design-tool-guide',
                'excerpt': 'Learn how to create stunning packaging designs using our free online design tool.',
                'content': '''<h2>Online Design Tool Guide</h2>
<p>Don't have design software? No problem! Our free online tool makes it easy to create professional designs.</p>

<h3>Getting Started</h3>
<ol>
    <li>Select your product and customize specs</li>
    <li>Click "Design Online" to launch the tool</li>
    <li>Choose a template or start from scratch</li>
</ol>

<h3>Key Features</h3>
<ul>
    <li><strong>Templates</strong> - Industry-specific starting points</li>
    <li><strong>Image Upload</strong> - Add your logo and photos</li>
    <li><strong>Text Tool</strong> - Add text with various fonts</li>
    <li><strong>Shapes</strong> - Basic shapes and design elements</li>
    <li><strong>Color Picker</strong> - Exact color matching</li>
    <li><strong>3D Preview</strong> - See your design on the actual product</li>
</ul>

<h3>Tips for Best Results</h3>
<ul>
    <li>Upload high-resolution images</li>
    <li>Use our safe zone guides</li>
    <li>Preview in 3D before ordering</li>
    <li>Save your design for future edits</li>
</ul>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': False,
                'tags': 'design tool, online designer, templates, create design',
            },
            
            # Shipping & Delivery
            {
                'category': 'shipping-delivery',
                'title': 'Shipping Options & Delivery Times',
                'slug': 'shipping-options',
                'excerpt': 'Learn about our shipping methods, delivery timeframes, and how to track your order.',
                'content': '''<h2>Shipping & Delivery</h2>
<p>We offer multiple shipping options to meet your timeline and budget.</p>

<h3>Production Times</h3>
<table>
    <tr><th>Order Type</th><th>Production Time</th></tr>
    <tr><td>Standard</td><td>10-15 business days</td></tr>
    <tr><td>Rush</td><td>5-7 business days (+25%)</td></tr>
    <tr><td>Express</td><td>3-5 business days (+50%)</td></tr>
</table>

<h3>Shipping Methods</h3>
<ul>
    <li><strong>Ground Shipping</strong> - 5-7 business days</li>
    <li><strong>Express</strong> - 2-3 business days</li>
    <li><strong>Overnight</strong> - Next business day</li>
</ul>

<h3>Free Shipping</h3>
<p>Orders over $500 qualify for free ground shipping within the continental US.</p>

<h3>Tracking Your Order</h3>
<p>Once shipped, you'll receive a tracking number via email. Track your shipment in real-time from your account dashboard.</p>

<h3>International Shipping</h3>
<p>We ship worldwide! International orders typically arrive within 7-21 business days depending on destination.</p>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'shipping, delivery, tracking, timeline, express, international',
            },
            {
                'category': 'shipping-delivery',
                'title': 'International Shipping Guide',
                'slug': 'international-shipping',
                'excerpt': 'Everything you need to know about ordering and shipping internationally with Packaxis.',
                'content': '''<h2>International Shipping</h2>
<p>We proudly ship to over 100 countries worldwide.</p>

<h3>Supported Countries</h3>
<p>We ship to most countries in:</p>
<ul>
    <li>North America (Canada, Mexico)</li>
    <li>Europe (EU countries, UK, Switzerland)</li>
    <li>Asia Pacific (Australia, Japan, Singapore, etc.)</li>
    <li>South America</li>
    <li>Middle East</li>
</ul>

<h3>Shipping Costs</h3>
<p>International shipping is calculated based on:</p>
<ul>
    <li>Package weight and dimensions</li>
    <li>Destination country</li>
    <li>Shipping speed selected</li>
</ul>

<h3>Customs & Duties</h3>
<p>International orders may be subject to customs duties and taxes. These are the responsibility of the recipient and are not included in our shipping charges.</p>

<h3>Delivery Times</h3>
<table>
    <tr><th>Region</th><th>Standard</th><th>Express</th></tr>
    <tr><td>Canada</td><td>7-10 days</td><td>3-5 days</td></tr>
    <tr><td>Europe</td><td>10-14 days</td><td>5-7 days</td></tr>
    <tr><td>Asia Pacific</td><td>14-21 days</td><td>7-10 days</td></tr>
</table>''',
                'difficulty': 'intermediate',
                'is_featured': False,
                'is_popular': False,
                'tags': 'international, global shipping, customs, duties, worldwide',
            },
            
            # Returns & Issues
            {
                'category': 'returns-issues',
                'title': 'Return Policy & Quality Guarantee',
                'slug': 'return-policy',
                'excerpt': 'Our commitment to quality and what to do if something isn\'t right with your order.',
                'content': '''<h2>Quality Guarantee</h2>
<p>We stand behind the quality of every product we produce.</p>

<h3>Our Promise</h3>
<p>If your order arrives damaged, defective, or doesn't match your approved proof, we will:</p>
<ul>
    <li>Reprint your order at no charge, OR</li>
    <li>Provide a full refund</li>
</ul>

<h3>How to Report an Issue</h3>
<ol>
    <li>Contact us within 14 days of delivery</li>
    <li>Provide your order number</li>
    <li>Include photos of the issue</li>
    <li>We'll respond within 24 hours</li>
</ol>

<h3>What's Covered</h3>
<ul>
    <li>Print quality defects</li>
    <li>Color mismatches (beyond CMYK tolerance)</li>
    <li>Structural defects</li>
    <li>Shipping damage</li>
    <li>Wrong items shipped</li>
</ul>

<h3>What's Not Covered</h3>
<ul>
    <li>Issues with customer-supplied artwork</li>
    <li>Color variations due to RGB to CMYK conversion</li>
    <li>Minor variations within industry standards</li>
</ul>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'returns, refund, quality, guarantee, damaged, defective',
            },
            
            # Sustainability
            {
                'category': 'sustainability',
                'title': 'Our Eco-Friendly Packaging Options',
                'slug': 'eco-friendly-packaging',
                'excerpt': 'Discover our sustainable packaging solutions and environmental certifications.',
                'content': '''<h2>Sustainable Packaging</h2>
<p>We're committed to helping brands reduce their environmental impact.</p>

<h3>Eco-Friendly Materials</h3>
<ul>
    <li><strong>Recycled Cardboard</strong> - Made from 100% post-consumer waste</li>
    <li><strong>FSC Certified Paper</strong> - From responsibly managed forests</li>
    <li><strong>Soy-Based Inks</strong> - Renewable, biodegradable printing</li>
    <li><strong>Water-Based Coatings</strong> - Non-toxic, eco-friendly finishes</li>
</ul>

<h3>Certifications</h3>
<ul>
    <li>FSC Chain of Custody Certified</li>
    <li>SFI Certified</li>
    <li>Recyclable packaging guarantee</li>
</ul>

<h3>Reducing Waste</h3>
<p>We optimize every production run to minimize waste:</p>
<ul>
    <li>Efficient die layouts</li>
    <li>Scrap recycling programs</li>
    <li>Right-sized packaging recommendations</li>
</ul>

<h3>Carbon Offset Program</h3>
<p>Add carbon offset to your order for just 1% of your order total. We'll plant trees to offset the carbon footprint of your packaging.</p>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': True,
                'tags': 'eco-friendly, sustainable, recycled, FSC, green, environment',
            },
            
            # Business & Enterprise
            {
                'category': 'business-enterprise',
                'title': 'Enterprise Account Benefits',
                'slug': 'enterprise-accounts',
                'excerpt': 'Learn about our enterprise program and the exclusive benefits for high-volume customers.',
                'content': '''<h2>Enterprise Accounts</h2>
<p>For businesses ordering regularly, our enterprise program offers exclusive benefits.</p>

<h3>Benefits</h3>
<ul>
    <li><strong>Volume Pricing</strong> - Up to 40% off standard rates</li>
    <li><strong>Net 30 Terms</strong> - Flexible payment terms</li>
    <li><strong>Dedicated Account Manager</strong> - Personal point of contact</li>
    <li><strong>Priority Production</strong> - Move to the front of the queue</li>
    <li><strong>Inventory Management</strong> - Store products at our facility</li>
    <li><strong>API Access</strong> - Integrate with your systems</li>
</ul>

<h3>Qualification</h3>
<p>Enterprise accounts are available for businesses that:</p>
<ul>
    <li>Place regular monthly orders, OR</li>
    <li>Have annual packaging spend of $50,000+</li>
</ul>

<h3>How to Apply</h3>
<ol>
    <li>Contact our enterprise sales team</li>
    <li>Complete the application form</li>
    <li>Credit approval (2-3 business days)</li>
    <li>Account activation</li>
</ol>''',
                'difficulty': 'intermediate',
                'is_featured': True,
                'is_popular': False,
                'tags': 'enterprise, business, wholesale, volume, B2B',
            },
            
            # Technical Support
            {
                'category': 'technical-support',
                'title': 'Browser & System Requirements',
                'slug': 'system-requirements',
                'excerpt': 'Ensure your system meets our requirements for the best experience using Packaxis.',
                'content': '''<h2>System Requirements</h2>
<p>For the best experience on Packaxis, ensure your system meets these requirements.</p>

<h3>Supported Browsers</h3>
<ul>
    <li>Google Chrome (recommended) - version 90+</li>
    <li>Mozilla Firefox - version 88+</li>
    <li>Safari - version 14+</li>
    <li>Microsoft Edge - version 90+</li>
</ul>

<h3>Design Tool Requirements</h3>
<p>Our online design tool requires:</p>
<ul>
    <li>WebGL enabled browser</li>
    <li>Minimum 4GB RAM</li>
    <li>Stable internet connection</li>
    <li>JavaScript enabled</li>
</ul>

<h3>File Upload Limits</h3>
<ul>
    <li>Maximum file size: 100MB</li>
    <li>Supported formats: AI, PDF, PSD, PNG, JPG</li>
</ul>

<h3>Troubleshooting</h3>
<p>If you experience issues:</p>
<ol>
    <li>Clear browser cache and cookies</li>
    <li>Disable browser extensions</li>
    <li>Try a different browser</li>
    <li>Contact support if issues persist</li>
</ol>''',
                'difficulty': 'beginner',
                'is_featured': False,
                'is_popular': False,
                'tags': 'browser, system requirements, technical, compatibility',
            },
            
            # Trust & Safety
            {
                'category': 'trust-safety',
                'title': 'How We Protect Your Data',
                'slug': 'data-protection',
                'excerpt': 'Learn about our security measures and how we keep your information safe.',
                'content': '''<h2>Data Protection & Security</h2>
<p>Your security is our priority. Here's how we protect your data.</p>

<h3>Encryption</h3>
<ul>
    <li>256-bit SSL encryption for all connections</li>
    <li>Encrypted database storage</li>
    <li>Secure payment processing via Stripe</li>
</ul>

<h3>Data Storage</h3>
<ul>
    <li>Servers located in secure US data centers</li>
    <li>Regular security audits</li>
    <li>Daily encrypted backups</li>
</ul>

<h3>Privacy Commitment</h3>
<ul>
    <li>We never sell your personal data</li>
    <li>Your designs remain your property</li>
    <li>Automatic design deletion after 12 months of inactivity</li>
</ul>

<h3>Compliance</h3>
<ul>
    <li>GDPR compliant</li>
    <li>CCPA compliant</li>
    <li>PCI DSS Level 1 (payment security)</li>
</ul>

<h3>Your Rights</h3>
<p>You can request to view, export, or delete your data at any time from your account settings.</p>''',
                'difficulty': 'beginner',
                'is_featured': True,
                'is_popular': False,
                'tags': 'security, privacy, data protection, GDPR, encryption',
            },
        ]

        # Create articles
        for article_data in articles_data:
            category_slug = article_data.pop('category')
            category = created_categories.get(category_slug)
            
            article, created = HelpArticle.objects.update_or_create(
                slug=article_data['slug'],
                defaults={
                    **article_data,
                    'category': category,
                    'status': 'published',
                    'is_active': True,
                    'published_at': timezone.now(),
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} article: {article.title}')

        self.stdout.write(self.style.SUCCESS(f'\nHelp Center seeded successfully!'))
        self.stdout.write(f'Categories: {HelpCategory.objects.count()}')
        self.stdout.write(f'Articles: {HelpArticle.objects.count()}')
