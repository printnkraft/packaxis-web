"""
Custom Django admin dashboards and analytics for Packaxis Packaging Canada.
Provides revenue tracking, order analytics, inventory management, and data exports.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.views.decorators.cache import cache_page
from django.template.response import TemplateResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
import csv
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from apps.orders.models import Order, OrderLine
from apps.products.models import Product, Category, ProductVariant
from apps.accounts.models import User
from apps.payments.models import Payment


class AdminDashboardMixin:
    """Base mixin for admin dashboard customization."""
    
    def get_urls(self):
        """Add custom admin dashboard URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
            path('revenue-export/', self.admin_site.admin_view(self.export_revenue_csv), name='revenue_export'),
            path('orders-export/', self.admin_site.admin_view(self.export_orders_csv), name='orders_export'),
            path('customers-export/', self.admin_site.admin_view(self.export_customers_csv), name='customers_export'),
        ]
        return custom_urls + urls
    
    @cache_page(60 * 5)  # Cache for 5 minutes
    def dashboard_view(self, request):
        """Main admin dashboard with analytics."""
        # Time period calculations
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Revenue metrics
        total_revenue = Order.objects.filter(
            status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        month_revenue = Order.objects.filter(
            created_at__date__gte=month_ago,
            status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        week_revenue = Order.objects.filter(
            created_at__date__gte=week_ago,
            status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        # Order metrics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='PENDING').count()
        processing_orders = Order.objects.filter(status='PROCESSING').count()
        
        # Customer metrics
        total_customers = User.objects.filter(role__in=['B2C', 'B2B']).count()
        b2b_customers = User.objects.filter(role='B2B').count()
        new_customers = User.objects.filter(
            role__in=['B2C', 'B2B'],
            created_at__date__gte=month_ago
        ).count()
        
        # Product metrics
        total_products = Product.objects.count()
        low_stock = ProductVariant.objects.filter(stock__lt=F('stock_minimum')).count()
        
        # Payment metrics
        successful_payments = Payment.objects.filter(status='CAPTURED').count()
        failed_payments = Payment.objects.filter(status='FAILED').count()
        
        # Recent orders
        recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
        
        # Top products
        top_products = Product.objects.annotate(
            total_sold=Count('orderline')
        ).order_by('-total_sold')[:5]
        
        context = {
            'title': 'Packaxis Packaging Canada Admin Dashboard',
            'total_revenue': f"${total_revenue:,.2f}",
            'month_revenue': f"${month_revenue:,.2f}",
            'week_revenue': f"${week_revenue:,.2f}",
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'total_customers': total_customers,
            'b2b_customers': b2b_customers,
            'new_customers': new_customers,
            'total_products': total_products,
            'low_stock': low_stock,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'recent_orders': recent_orders,
            'top_products': top_products,
        }
        
        return TemplateResponse(
            request,
            'admin/dashboard.html',
            context
        )
    
    def export_revenue_csv(self, request):
        """Export revenue report as CSV."""
        response = admin.HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="revenue_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Orders', 'Revenue', 'Avg Order Value', 'Stripe', 'PayPal'])
        
        # Aggregate by date
        orders = Order.objects.filter(
            status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
        ).values('created_at__date').annotate(
            count=Count('id'),
            total=Sum('total')
        ).order_by('created_at__date')
        
        for order in orders:
            date = order['created_at__date']
            order_count = order['count']
            revenue = order['total']
            avg_value = revenue / order_count if order_count > 0 else 0
            
            stripe = Payment.objects.filter(
                created_at__date=date,
                method='stripe',
                status='CAPTURED'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            paypal = Payment.objects.filter(
                created_at__date=date,
                method='paypal',
                status='CAPTURED'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            writer.writerow([date, order_count, f"{revenue:,.2f}", f"{avg_value:,.2f}", 
                           f"{stripe:,.2f}", f"{paypal:,.2f}"])
        
        return response
    
    def export_orders_csv(self, request):
        """Export orders report as CSV."""
        response = admin.HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order #', 'Customer', 'Email', 'Date', 'Total', 'Items', 'Status', 'Payment'])
        
        orders = Order.objects.select_related('customer').order_by('-created_at')
        for order in orders:
            writer.writerow([
                order.order_number,
                order.customer.get_full_name() or order.customer.email,
                order.customer.email,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                f"{order.total:,.2f}",
                order.orderline_set.count(),
                order.status,
                Payment.objects.filter(order=order).first().method if Payment.objects.filter(order=order).exists() else 'N/A'
            ])
        
        return response
    
    def export_customers_csv(self, request):
        """Export customers report as CSV."""
        response = admin.HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Type', 'Company', 'Orders', 'Total Spent', 'Joined'])
        
        customers = User.objects.filter(role__in=['B2C', 'B2B'])
        for customer in customers:
            total_spent = Order.objects.filter(
                customer=customer,
                status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
            ).aggregate(Sum('total'))['total__sum'] or 0
            
            order_count = Order.objects.filter(customer=customer).count()
            
            writer.writerow([
                customer.email,
                customer.get_full_name() or 'N/A',
                customer.role,
                customer.company_name or 'N/A',
                order_count,
                f"{total_spent:,.2f}",
                customer.created_at.strftime('%Y-%m-%d')
            ])
        
        return response


class DashboardAdminSite(admin.AdminSite):
    """Custom admin site with dashboard integration."""
    site_header = "Packaxis Packaging Canada Admin"
    site_title = "Packaxis Packaging Canada"
    index_title = "Dashboard & Analytics"
    
    def index(self, request, extra_context=None):
        """Override default admin index to show dashboard."""
        # Redirect to dashboard
        from django.shortcuts import redirect
        return redirect('admin:dashboard')
