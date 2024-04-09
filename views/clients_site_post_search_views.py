from uuid import uuid4
from django.core.files.base import ContentFile
from rest_framework.response import Response
from AuthGuard.utils import WatchDogMixin
from Blog.serializers.post_create_view_serializers import ExternalPostSerializer
from Blog.models import *
from rest_framework import generics, status
from ServiceHub.utils.custom_pagination_util import CustomPagination
from django.db.models import Q
from rest_framework import generics


class PostGlobalSearchView(generics.ListAPIView):
   

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')

        # Perform search across multiple models
        external_posts = ExternalPostModel.objects.filter(
            Q(category__icontains=query) |
            Q(url__icontains=query) |
            Q(title__icontains=query)
        )
        post_contents = PostContentModel.objects.filter(
            Q(content__icontains=query) |
            Q(image__icontains=query) |
            Q(video__icontains=query)
        )
        posts = PostModel.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__category__icontains=query) | 
            Q(sub_categories__sub_category__icontains=query) |  
            Q(keywords__icontains=query)
        )

        # Combine the results
        results = list(external_posts) + list(post_contents) + list(posts)

        # Serialize the results
        serialized_results = []

        for result in results:
            if isinstance(result, ExternalPostModel):
                serialized_results.append({
                    'type': 'external_post',
                    'id': result.id,
                    'title': result.title,
                    'url': result.url,
                    'category': result.category,
                })
            elif isinstance(result, PostContentModel):
                serialized_results.append({
                    'type': 'post_content',
                    'id': result.id,
                    'content': result.content,
                    'image': result.image,
                    'video': result.video,
                })
            elif isinstance(result, PostModel):
                serialized_results.append({
                    'type': 'post',
                    'id': result.id,
                    'title': result.title,
                    'short_description': result.short_description,
                    'category': result.category,
                    'sub_categories': result.sub_categories,
                    'keywords': result.keywords,
                })
            return Response(serialized_results, status=status.HTTP_200_OK)