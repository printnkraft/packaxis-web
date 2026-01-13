from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, BlogCategory, BlogPost, FAQCategory, FAQ, FooterSection, HelpCategory, HelpArticle, HelpArticleSearch


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'url', 'order', 'is_active', 'parent')
    list_filter = ('location', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'url')
    ordering = ('location', 'order')


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active', 'is_featured')


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


class HelpArticleInline(admin.TabularInline):
    model = HelpArticle
    extra = 0
    fields = ('title', 'status', 'order', 'is_featured')
    readonly_fields = ('title',)
    show_change_link = True


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_display', 'color_display', 'article_count_display', 'order', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_editable = ('order', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'order', 'is_active', 'is_featured'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

    inlines = [HelpArticleInline]

    def icon_display(self, obj):
        return format_html('<span class="material-symbols-rounded">{}</span> {}', obj.icon, obj.icon)
    icon_display.short_description = 'Icon'

    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border-radius: 4px; border: 1px solid #ccc;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'

    def article_count_display(self, obj):
        count = obj.article_count
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return count
    article_count_display.short_description = 'Articles'


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'difficulty', 'order', 'is_featured', 'is_popular', 'views_count')
    list_filter = ('status', 'category', 'difficulty', 'is_featured', 'is_popular')
    list_editable = ('order', 'is_featured', 'is_popular')
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('views_count', 'helpful_yes', 'helpful_no', 'created_at', 'updated_at')
    filter_horizontal = ('related_articles',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Organization', {
            'fields': ('order', 'difficulty', 'estimated_read_time', 'tags')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_featured', 'is_popular', 'published_at')
        }),
        ('Related Content', {
            'fields': ('related_articles',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views_count', 'helpful_yes', 'helpful_no'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HelpArticleSearch)
class HelpArticleSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'results_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query',)
    date_hierarchy = 'created_at'
    readonly_fields = ('query', 'results_count', 'session_id', 'ip_address', 'created_at')
