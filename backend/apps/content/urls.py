from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/search/', views.blog_search, name='blog_search'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # FAQ URLs
    path('faq/', views.faq_list, name='faq_list'),
    
    # Contact URL
    path('contact/', views.contact_page, name='contact'),
    
    # Help Center URLs
    path('help/', views.help_center, name='help_center'),
    path('help/search/', views.help_search, name='help_search'),
    path('help/category/<slug:slug>/', views.help_category, name='help_category'),
    path('help/article/<slug:slug>/', views.help_article, name='help_article'),
    path('help/article/<slug:slug>/feedback/', views.help_article_feedback, name='help_article_feedback'),
]
