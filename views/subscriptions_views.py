from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import *
from Blog.serializers.post_subscribtions_serializers import *
from Blog.models import *
from rest_framework import generics
from AuthGuard.utils.auth_handler_util import WatchDogMixin
from django.db.models import Sum
from rest_framework.generics import CreateAPIView
from django.db.models import Q
from django.db.models import Count
from bs4 import BeautifulSoup
from ServiceHub.utils.custom_pagination_util import CustomPagination


class SubscriptionCreateView ( WatchDogMixin,CreateAPIView, generics.GenericAPIView):
    """ Create a new subscription for the user."""
    
    serializer_class = SubscriptionSerializer
    
    
    def post(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            serializer = SubscriptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            subscription = SubscriptionModel.objects.all()
            serializer = SubscriptionSerializer(subscription, many=True)
            return Response({
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            user = request.user
            subscription = SubscriptionModel.objects.filter(user=user)
            subscription.delete()
            return Response({
                "status": "success",
                "message": "Subscription deleted successfully",
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        
            
              
class SubscriptionListView(WatchDogMixin, generics.ListAPIView):
    """ List all subscriptions for the user."""
    
    serializer_class = SubscriptionListSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        self.get_authenticated_user()
        queryset = SubscriptionModel.objects.all()

        # Filter by from and to date
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date and to_date:
            queryset = queryset.filter(created_at__range=[from_date, to_date])

        # Filter by site name
        site = self.request.query_params.get('site')
        if site:
            queryset = queryset.filter(Q(source__icontains=site) | Q(source__icontains=site.capitalize()))
        # make a case insensitive search for all the data
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(source__icontains=search))
        # Filter by activated subscribers or unsubscribed subscribers
        subscription = self.request.query_params.get('subscription')
        if subscription == 'true':
            queryset = queryset.filter(activated=True)
        elif subscription == 'false':
            queryset = queryset.filter(activated=False)

        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            queryset = self.get_queryset()
            total_count = queryset.count() 
            paginator = self.pagination_class()
            queryset = paginator.paginate_queryset(queryset, request)
            serializer = SubscriptionListSerializer(queryset, many=True)
            respone_data = serializer.data
            respone_data.append({'total_count': total_count})
            return paginator.get_paginated_response(respone_data)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
class SubscriptionUnsubscribeView(WatchDogMixin, generics.RetrieveUpdateAPIView):
    """ Unsubscribe from the subscription."""
    
    queryset = SubscriptionModel.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            instance.activated = False
            instance.save(update_fields=['activated', 'updated_at'])
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "Unsubscribed successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)