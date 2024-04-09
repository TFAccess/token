import base64
from uuid import uuid4
from django.core.files.base import ContentFile
from rest_framework.response import Response
from AuthGuard.utils import WatchDogMixin
from Blog.serializers.post_create_view_serializers import ExternalPostSerializer
from Blog.models import *
from rest_framework import generics, status
from ServiceHub.utils.custom_pagination_util import CustomPagination






class ExternalPostCreateView (WatchDogMixin, generics.CreateAPIView):
    serializer_class = ExternalPostSerializer

    def create(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            image = request.data.get('image')
            logo = request.data.get('logo')
            if image:
            
                format, imgstr = image.split(';base64,')
                ext = format.split('/')[-1]
                unique_filename = f"{uuid4()}.{ext}" 
                data = ContentFile(base64.b64decode(imgstr), name=unique_filename)
                request.data['image'] = data
            if logo:
                format, imgstr = logo.split(';base64,')
                ext = format.split('/')[-1]
                unique_filename = f"{uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=unique_filename)
                request.data['logo'] = data
            return super().create(request, *args, **kwargs)
        
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class ExternalPostListView (WatchDogMixin, generics.ListAPIView):
    serializer_class = ExternalPostSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # add filter to cateogry with news and  author
        queryset = ExternalPostModel.objects.all()
        
        ceo = self.request.query_params.get('ceo', None)
        if ceo is not None:
            queryset = queryset.filter(category=ceo)
        news = self.request.query_params.get('news', None)
        if news is not None:
            queryset = queryset.filter(news=news)
        return queryset
    
       
    def list(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            queryset = self.get_queryset().order_by('-created_at')
            serializer = ExternalPostSerializer(queryset, many=True)
            page = self.paginate_queryset(serializer.data)
            Pagination = self.get_paginated_response(page).data
            return Response({"status": True, "data": Pagination}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ExternalPostDetailView (WatchDogMixin, generics.RetrieveUpdateDestroyAPIView):
    
    queryset = ExternalPostModel.objects.all()
    serializer_class = ExternalPostSerializer
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            image_data = request.data.get('image')
            logo_data = request.data.get('logo')

            # Function to convert base64 data to file
            def base64_to_file(base64_data, filename):
                format, imgstr = base64_data.split(';base64,')
                ext = format.split('/')[-1]
                return ContentFile(base64.b64decode(imgstr), name=f"{filename}.{ext}")

            instance = self.get_object()
            # Decode and update the image if a new one is provided
            if image_data and image_data.startswith('data:image'):
                request.data['image'] = base64_to_file(image_data, 'image')
            
            else:
                request.data['image'] = instance.image

           
            if logo_data and logo_data.startswith('data:image'):
                request.data['logo'] = base64_to_file(logo_data, 'logo')
                
            else:
                request.data['logo'] = instance.logo

            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        
    def destroy(self, request, *args, **kwargs):    
        try:
            self.get_authenticated_user()
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ExternalPostViewerCountView (WatchDogMixin, generics.RetrieveUpdateAPIView):
    queryset = ExternalPostModel.objects.all()
    serializer_class = ExternalPostSerializer
    lookup_field = 'pk'
    # print(f"lookup_fields: {lookup_field}")
    def retrieve(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    def update(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            instance.views += 1
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        return Response({"status": False, "msg": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)