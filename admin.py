from django.contrib import admin

# Register your models here.
from .models import  *



@admin.register(PostedSiteModel)
class PostedSiteModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "posted_site", "site_url"
    ]

@admin.register(BlogCategoryModel)
class BlogCategoryModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "posted_site", "category"
    ]
@admin.register(BlogSubCategoryModel)

class BlogSubCategoryModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "category", "sub_category"
    ]
    
@admin.register(PostModel)
class PostModelAdmin(admin.ModelAdmin):
    # all fields
    list_display = [
        "id", "title", "category", "author"
    ]
@admin.register(PostContentModel)
class PostContentModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "post", "content", "image", "video", "tracking","alignment"
    ]
    
    
@admin.register(CommentModel)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "post", "comment"
    ]
    

    
@admin.register(FilterOptionModel)
class FilterOptionModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "filter_name"
    ]
    

@admin.register(SubscriptionModel)
class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "email", "source"
    ]