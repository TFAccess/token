# serializers.py
import re
from rest_framework import serializers
from Blog.models import *
import base64
from django.core.files.base import ContentFile
class PostContentSerializer(serializers.ModelSerializer):
    
    """ Serializer for PostContentModel"""
    class Meta:
        model = PostContentModel
        fields = ['content', 'image', 'video', 'tracking', 'alignment', 'padding_top', 'padding_bottom', 'padding_left', 'padding_right']
        
        

class SiteNameSerializer(serializers.ModelSerializer):
    
    """ Serializer for SiteNameModel """
    # add site_logo with base url
   
    site_logo = serializers.SerializerMethodField("get_site_logo")
    
    def get_site_logo(self, obj):
        request = self.context["request"]
        site_logo = PostedSiteModel.objects.get(pk=obj.id).site_logo
        if site_logo:
            return request.build_absolute_uri(site_logo.url)
        else:
            return None
    class Meta:
        model = PostedSiteModel
        fields = ['posted_site', 'site_url', 'site_logo',]

class SiteNamecreateSerializer(serializers.ModelSerializer):
      
    class Meta:
        model = PostedSiteModel
        fields = "__all__"
        
        
class PostSerializer(serializers.ModelSerializer):
    
    """ Serializer for PostModel"""
  
    keywords = serializers.ListField(child=serializers.CharField(max_length=255), allow_empty=True, required=False)    
    
    class Meta:
        model = PostModel
        fields = "__all__"

class PageSerializer(serializers.ModelSerializer):
        
        """ Serializer for PageModel """
        class Meta:
            model = PostModel
            fields = "__all__"

class BlogSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSubCategoryModel
        fields = ['sub_category']

class BlogCategorySerializer(serializers.ModelSerializer):
    sub_category = BlogSubCategorySerializer(many=True)

    class Meta:
        model = BlogCategoryModel
        fields = ['posted_site', 'category', 'sub_category']

    def create(self, validated_data):
        
        """ Create a new category and its subcategories."""
      
        posted_site_pk = validated_data.pop('posted_site')
        posted_site_id = posted_site_pk.id
        posted_site_instance = PostedSiteModel.objects.get(pk=posted_site_id)

        subcategories_data = validated_data.pop('sub_category', [])
    
        validated_data['posted_site'] = posted_site_instance
        category = BlogCategoryModel.objects.create(**validated_data)

        for subcategory_data in subcategories_data:
            BlogSubCategoryModel.objects.create(category=category, **subcategory_data)

        return category
    
    def update(self, instance, validated_data):
        
            """ Update an existing category and its subcategories."""
           
            subcategories_data = validated_data.pop('sub_category', [])
            subcategories = list(instance.sub_category.all())
            instance.category = validated_data.get('category', instance.category)
            posted_site_pk = validated_data.pop('posted_site')
            if posted_site_pk:
                posted_site_id = posted_site_pk.id
                posted_site_instance = PostedSiteModel.objects.get(pk=posted_site_id)
                instance.posted_site = posted_site_instance
            instance.save()

            # List to keep track of subcategories to delete
            subcategories_to_delete = []

            for subcategory_data in subcategories_data:
                if subcategories:
                    subcategory = subcategories.pop(0)
                    subcategory.sub_category = subcategory_data.get('sub_category', subcategory.sub_category)
                    subcategory.save()
                else:
                
                    BlogSubCategoryModel.objects.create(category=instance, **subcategory_data)

            # Mark remaining subcategories to delete
            for subcategory in subcategories:
                subcategories_to_delete.append(subcategory.id)

            # Delete marked subcategories
            BlogSubCategoryModel.objects.filter(id__in=subcategories_to_delete).delete()

            return instance
    class TableofContentSerializer(serializers.ModelSerializer):
        
        """ Serializer for TableOfContentModel """
        class Meta:
            model = TableofContentModel
            fields = ['title', 'link'] 
            

class ExternalPostSerializer(serializers.ModelSerializer):
    
    """ Serializer for ExternalPostModel """
    class Meta:
        model = ExternalPostModel
        fields = "__all__"