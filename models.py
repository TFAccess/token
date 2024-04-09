


from django.db import models
# Create your models here.
from Account.models import User
from django.utils import timezone
from tinymce.models import HTMLField
import datetime

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

# Create your models here.
COMMENT_OPTIONS = (
    ('disabled', 'Disable Comments'),
    ('enabled', 'Enable Comments'),
)
class PostedSiteModel(models.Model):
    posted_site= models.CharField(max_length=100)
    site_url = models.URLField()
    site_logo = models.FileField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Posted Site'
        
    def __str__(self):
        return self.posted_site

class BlogCategoryModel(models.Model):
    
    posted_site = models.ForeignKey(PostedSiteModel, on_delete=models.CASCADE, related_name='site_category')
    category = models.CharField(max_length=80)
    class Meta:
        verbose_name_plural = 'Blog Category'
        
    def __str__(self):
        return self.category

class BlogSubCategoryModel(models.Model):
    category = models.ForeignKey(BlogCategoryModel, on_delete=models.CASCADE, related_name='sub_category')
    sub_category = models.CharField(max_length=80)
    class Meta:
        verbose_name_plural = 'Blog Sub Category'
        
        
    def __str__(self):
        return self.sub_category

  
        


class FilterOptionModel(models.Model):
    sub_category = models.ManyToManyField(BlogSubCategoryModel, related_name='filter_subcategory', blank=True)
    filter_name = models.CharField(max_length=80)

    def __str__(self):
        return self.filter_name

    class Meta:
        verbose_name_plural = 'Blog Filter Option'

class PostModel(models.Model):
    author = models.ForeignKey(User, verbose_name=_('Author'), on_delete=models.CASCADE, null=True, blank=True)
    post_url = models.CharField(max_length=255, verbose_name=_('URL'), unique=True)
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    short_description = models.TextField( max_length=255 , blank=True, null=True)
    category = models.ForeignKey(BlogCategoryModel, on_delete=models.CASCADE, related_name='post_category')
    sub_categories = models.ForeignKey(BlogSubCategoryModel, on_delete=models.CASCADE, related_name='post_sub_category',
                                       blank=True, null=True)
    filter_option = models.ForeignKey(FilterOptionModel, on_delete=models.CASCADE, related_name='post_filter',
                                      blank=True, null=True)
    # Add fields for featured image and its metadata
    feature_image = models.FileField(upload_to='blog/', blank=True, null=True)
    feature_image_title = models.CharField(max_length=255,  blank=True, null=True)
    feature_image_alt_text = models.CharField(max_length=255, blank=True, null=True)
    posted_sites = models.ManyToManyField(PostedSiteModel, related_name='posts', verbose_name=_('Posted Sites'))
    reading_time = models.DurationField(default=datetime.timedelta(minutes=3))
    comment_option = models.CharField(choices=COMMENT_OPTIONS, default='disabled', max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    total_view = models.IntegerField(blank=True, default=0)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    schema_data = models.JSONField(null=True, blank=True) 
    
    class Meta:
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # create schema data       
        self.schema_data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": self.title,
            "image": self.feature_image.url,
            "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
            "dateModified": datetime.datetime.now().strftime("%Y-%m-%d"),
            "author": {
                "@type": "Person",
                "name": self.author.full_name
            },
            "publisher": {
                "@type": "Organization",
                "name": "Tech Blog",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://example.com/logo.jpg"
                }
            },
            "description": self.short_description,
            "articleBody": self.short_description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": "https://google.com"
            }
        }
        super(PostModel, self).save(*args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     # Create the initial schema data
    #     initial_schema_data = {
    #         "@context": "https://schema.org",
    #         "@type": "BlogPosting",
    #         "headline": self.title,
    #         "image": self.feature_image.url,
    #         "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
    #         "dateModified": datetime.datetime.now().strftime("%Y-%m-%d"),
    #         "author": {
    #             "@type": "Person",
    #             "name": self.author.full_name
    #         }
         
    #     }
    #     self.schema_data = initial_schema_data
    #     super(PostModel, self).save(*args, **kwargs)

    #     site_objects = PostedSiteModel.objects.filter(posts=self.post_url)
    #     print(f"site_objects: {site_objects}")
    #     for site in site_objects:
    #         self.schema_data.setdefault("publisher", {
    #             "@type": "Organization",
    #             "name": site.posted_site,
    #             "logo": {
    #                 "@type": "ImageObject",
    #                 "url": site.site_logo.url
    #             }
    #         })
      
    #     # Save the updated schema data
    #     self.save(update_fields=["schema_data"])

class PostedSiteTrackingModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='post_tracking')
    posted_site = models.ForeignKey(PostedSiteModel, on_delete=models.CASCADE, related_name='site_tracking')
    total_view = models.IntegerField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post.title}\'s tracking'

    class Meta:
        verbose_name_plural = 'Posted Site Tracking'
  
    
class CommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comment_post')
    comment = models.TextField(verbose_name='Comment', max_length=255)
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post.title}\'s comment'


reading_status = (
    ('read', 'Read'),
    ('unread', 'Unread'),
)


class ReadingListModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_list_user')
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='reading_list_post')
    added_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=reading_status, default='unread')

    def __str__(self):
        return f'{self.user} - {self.post}'


class SubscriptionModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    source = models.CharField(max_length=255, blank=True, null=True)
    activated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} ({self.email})'





    
TRACKING_CHOICES = (
    ('below_content', 'Below Content'),
    ('above_content', 'Above Content'),
    ('below_header', 'Below Header'),
)   
ALIGNMENT_CHOICES = (
    ('left', 'Left'),
    ('right', 'Right'),
    ('center', 'Center'),
    ('justify', 'Justify'),
) 
class PostContentModel(models.Model):
    content = HTMLField()
    # if not add image or video then it will be null
    image = models.FileField(upload_to='blog/', blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    tracking = models.CharField(max_length=100, choices=TRACKING_CHOICES, default='below_content')
    alignment = models.CharField(max_length=100, choices=ALIGNMENT_CHOICES, default='center')
    padding_top = models.IntegerField(default=0)
    padding_bottom = models.IntegerField(default=0)
    padding_left = models.IntegerField(default=0)
    padding_right = models.IntegerField(default=0)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='post_content')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Post Content'
        
    def __str__(self):
        return self.post.title

class TableofContentModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='post_table_of_content')
    title = models.CharField(max_length=255 , blank=True, null=True)
    link = models.CharField(max_length=255 , blank=True, null=True)
    activated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Table of Content'
        
    def __str__(self):
        return self.title
    
    
class ExternalPostModel(models.Model):
    CATEGORY_CHOICES = (
        ('news', 'News'),
        ('ceo', 'CEO'),
    )
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    url = models.URLField()
    image = models.FileField(upload_to='blog/', blank=True, null=True)
    logo = models.FileField(upload_to='blog/', blank=True, null=True)
    title = models.CharField(max_length=100)
    views = models.IntegerField(blank=True, default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
