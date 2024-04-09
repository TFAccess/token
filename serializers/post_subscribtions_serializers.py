import base64
import re
from rest_framework import serializers
from Blog.models import *
from urllib.parse import urlparse


class SubscriptionSerializer(serializers.ModelSerializer):
    
    """ Serializer for SubscriptionModel """
    
    class Meta:
        model = SubscriptionModel
        fields = "__all__"
        


class SubscriptionListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    visited_site = serializers.SerializerMethodField()
    source = serializers.CharField()
   

    class Meta:
        model = SubscriptionModel
        fields = [ 'id','name', 'email', 'visited_site', 'source', 'created_at','updated_at']

    def get_visited_site(self, obj):
        parsed_url = urlparse(obj.source)
        domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]
        return {'site': domain, 'url': parsed_url.netloc}


        