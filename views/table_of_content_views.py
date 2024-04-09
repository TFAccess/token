from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import *
from Blog.serializers.post_create_view_serializers import *
from Blog.models import *
from rest_framework import generics
from AuthGuard.utils.auth_handler_util import WatchDogMixin
from django.db.models import Sum
from rest_framework.generics import CreateAPIView
from django.db.models import Q
from django.db.models import Count
from bs4 import BeautifulSoup


from rest_framework.response import Response
from rest_framework import status

class PostViewWithTableofContentView(WatchDogMixin, generics.RetrieveAPIView):

    def get_serializer(self, *args, **kwargs):
        return None

    queryset = PostModel.objects.all()
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('pk')
            post = self.queryset.get(id=post_id)
            table_of_contents = TableofContentModel.objects.filter(post=post)
            table_of_contents_data = [{'id': toc.id, 'title': toc.title, 'link': toc.link, 'status': toc.activated} for toc in table_of_contents]
            response_data = {
                'post_id': post_id,
                'category': post.category.category,
                'post_title': post.title,
                "post_url": post.post_url,
                'feature_image': request.build_absolute_uri(post.feature_image.url) if post.feature_image else None,
                'post_content_with_media': self.generate_final_content(post, request),  # Pass request to the method
                'table_of_contents': table_of_contents_data,
                'related_posts': self.get_related_posts(post)
            }

            return Response(response_data)

        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def generate_final_content(self, post, request):
        content_with_media = []
        post_content_items = PostContentModel.objects.filter(post=post)
    
        for content in post_content_items:
            media_data = {
                'content': content.content,
                'image': request.build_absolute_uri(content.image.url) if content.image else None,
                'video': content.video,
                'tracking': content.tracking,
                'alignment': content.alignment,
                'padding_top': content.padding_top,
                'padding_bottom': content.padding_bottom,
                'padding_left': content.padding_left,
                'padding_right': content.padding_right
            }
            content_with_media.append(media_data)

        content_with_media.sort(key=lambda x: x['tracking'] != 'below_content')
        
        final_content = []
        
        for item in content_with_media:
            soup = BeautifulSoup(item['content'], 'html.parser')
            h1_tags = soup.find_all('h1')
          
            if item['tracking'] == 'above_content':
                if item['image']:
                    img_tag = soup.new_tag('img', src=item['image'])
                    soup.insert(0, img_tag)
                elif item['video']:
                    video_tag = soup.new_tag('iframe', src=item['video'])
                    soup.insert(0, video_tag)
             
            elif item['tracking'] == 'below_header' and h1_tags:
                first_h1_tag = h1_tags[0]
                if item['image']:
                    img_tag = soup.new_tag('img', src=item['image'])
                    first_h1_tag.insert_after(img_tag)
                elif item['video']:
                    video_tag = soup.new_tag('iframe', src=item['video'])
                    first_h1_tag.insert_after(video_tag)
           
            final_content.append(str(soup))
            
        return final_content

    def get_related_posts(self, post):
        related_posts = PostModel.objects.filter(category=post.category).exclude(id=post.id).order_by('-date')[:3]
        related_posts_data = []
        for p in related_posts:
            related_posts_data.append({'title': p.title, 'url': p.post_url})
            
        return related_posts_data