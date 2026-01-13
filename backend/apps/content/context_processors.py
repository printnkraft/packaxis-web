from .models import MenuItem, FooterSection


def dynamic_menu(request):
    """Add dynamic menu items to all templates"""
    return {
        'header_menu': MenuItem.objects.filter(
            location='header',
            is_active=True,
            parent=None
        ),
        'footer_main_menu': MenuItem.objects.filter(
            location='footer_main',
            is_active=True
        ),
        'footer_support_menu': MenuItem.objects.filter(
            location='footer_support',
            is_active=True
        ),
        'footer_legal_menu': MenuItem.objects.filter(
            location='footer_legal',
            is_active=True
        ),
        'footer_sections': FooterSection.objects.filter(is_active=True),
    }
