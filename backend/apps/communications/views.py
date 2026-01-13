from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json
import logging

from .models import NewsletterSubscriber

logger = logging.getLogger(__name__)


@require_POST
def contact_submit(request):
    """Handle contact form submission and send email to support"""
    try:
        data = json.loads(request.body)
        
        # Extract form data
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        company = data.get('company', '').strip()
        subject_type = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        newsletter = data.get('newsletter', False)
        
        # Validation
        errors = {}
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not email:
            errors['email'] = 'Email is required'
        if not subject_type:
            errors['subject'] = 'Please select a subject'
        if not message or len(message) < 20:
            errors['message'] = 'Message must be at least 20 characters'
            
        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        
        # Map subject types to readable labels
        subject_labels = {
            'quote': 'Request a Quote',
            'product': 'Product Inquiry',
            'order': 'Order Status',
            'custom': 'Custom Packaging',
            'wholesale': 'Wholesale Partnership',
            'support': 'Technical Support',
            'feedback': 'Feedback',
            'other': 'Other'
        }
        subject_label = subject_labels.get(subject_type, subject_type)
        
        # Build email content
        email_subject = f"[PackAxis Contact] {subject_label} - {first_name} {last_name}"
        email_body = f"""
New contact form submission from PackAxis website:

----------------------------------------
CONTACT DETAILS
----------------------------------------
Name: {first_name} {last_name}
Email: {email}
Phone: {phone or 'Not provided'}
Company: {company or 'Not provided'}

----------------------------------------
INQUIRY
----------------------------------------
Subject: {subject_label}

Message:
{message}

----------------------------------------
ADDITIONAL INFO
----------------------------------------
Newsletter Subscription: {'Yes' if newsletter else 'No'}
Submitted: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

----------------------------------------
This message was sent from the PackAxis contact form.
        """.strip()
        
        # Send email to support
        try:
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@packaxis.ca'],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send contact email: {e}")
            # Continue even if email fails - we'll log it
        
        # Handle newsletter subscription
        if newsletter and email:
            try:
                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={
                        'is_active': True,
                        'preferences': {
                            'source': 'contact_form',
                            'name': f'{first_name} {last_name}'
                        }
                    }
                )
                if not created and not subscriber.is_active:
                    # Reactivate if previously unsubscribed
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.save()
            except Exception as e:
                logger.error(f"Failed to add newsletter subscriber: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message! Our team will get back to you within 24 hours.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again or contact us directly.'
        }, status=500)


@require_POST  
def newsletter_subscribe(request):
    """Handle newsletter subscription from anywhere on the site"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        source = data.get('source', 'website')  # e.g., 'footer', 'popup', 'checkout'
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            }, status=400)
        
        # Basic email validation
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address'
            }, status=400)
        
        # Create or update subscriber
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'is_active': True,
                'preferences': {'source': source}
            }
        )
        
        if not created:
            if subscriber.is_active:
                return JsonResponse({
                    'success': True,
                    'message': 'You are already subscribed to our newsletter!'
                })
            else:
                # Reactivate
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.preferences['resubscribed_from'] = source
                subscriber.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! You have been resubscribed to our newsletter.'
                })
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for subscribing! You will receive our latest updates and offers.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Newsletter subscription error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)


@require_POST
def newsletter_unsubscribe(request):
    """Handle newsletter unsubscription"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            }, status=400)
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if subscriber.is_active:
                subscriber.is_active = False
                subscriber.unsubscribed_at = timezone.now()
                subscriber.save()
                return JsonResponse({
                    'success': True,
                    'message': 'You have been unsubscribed from our newsletter.'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'This email is already unsubscribed.'
                })
        except NewsletterSubscriber.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Email not found in our subscriber list.'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Newsletter unsubscription error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)
