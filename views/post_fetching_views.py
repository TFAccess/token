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
import requests




# class PostFetchView (WatchDogMixin, generics.RetrieveAPIView):
    
#     def get_serializer(self, *args, **kwargs):
#         return None
    
    
#     queryset = PostModel.objects.all()
#     lookup_field = 'pk'
    
    
#     def get(self, request, *args, **kwargs):
#             try:
#                 post_id = self.kwargs.get('pk')
#                 post = self.queryset.get(id=post_id)

#                 # Retrieve category
#                 category = post.category.category
                
#                 # Retrieve post title and content
#                 post_title = post.title
#                 feature_image = post.feature_image.url if post.feature_image else None
#                 realated_post = PostModel.objects.filter(category=post.category).exclude(id=post_id).order_by('-date')[:3]
#                 realated_post_data = []
#                 for p in realated_post:
#                     realated_post_data.append({'title': p.title, 'url': p.post_url})
        
#                 post_content_items = PostContentModel.objects.filter(post=post_id)
                
#                 content_with_media = []
#                 for content in post_content_items:
#                     media_data = {}
#                     media_data['content'] = content.content
#                     media_data['image'] = content.image.url if content.image else None
#                     media_data['video'] = content.video
#                     media_data['tracking'] = content.tracking
#                     media_data['alignment'] = content.alignment
#                     media_data['padding_top'] = content.padding_top
#                     media_data['padding_bottom'] = content.padding_bottom
#                     media_data['padding_left'] = content.padding_left
#                     media_data['padding_right'] = content.padding_right
#                     content_with_media.append(media_data)
                
#                 content_with_media.sort(key=lambda x: x['tracking'] != 'below_content')
                
#                 # Prepare final content
#                 final_content = []
#                 for item in content_with_media:
#                     soup = BeautifulSoup(item['content'], 'html.parser')
#                     h1_tags = soup.find_all('h1')
#                     # If 'above_content' tracking is selected, insert media before content
#                     if item['tracking'] == 'above_content':
#                         if item['image']:
#                             img_tag = soup.new_tag('img', src=item['image'])
#                             soup.insert(0, img_tag)
#                         elif item['video']:
#                             video_tag = soup.new_tag('iframe', src=item['video'])
#                             soup.insert(0, video_tag)
#                     # If 'below_header' tracking is selected, insert media after first h1 tag
#                     elif item['tracking'] == 'below_header' and h1_tags:
#                         first_h1_tag = h1_tags[0]
#                         if item['image']:
#                             img_tag = soup.new_tag('img', src=item['image'])
#                             first_h1_tag.insert_after(img_tag)
#                         elif item['video']:
#                             video_tag = soup.new_tag('iframe', src=item['video'])
#                             first_h1_tag.insert_after(video_tag)
#                     # Otherwise, keep content as is
#                     final_content.append(str(soup))
                
#                 # Generate table of contents from H1 tags

#                     table_of_contents = []
#                     for content in final_content:
#                         soup = BeautifulSoup(content, 'html.parser')
                        
#                         # Find all h1 tags
#                         h1_tags = soup.find_all('h1')
#                         for h1_tag in h1_tags:
#                             h1_title = h1_tag.text
#                             h1_link = f'#'
#                             h1_contents = []

#                             # Find all h2 tags within the current h1 tag
#                             h2_tags = h1_tag.find_next_siblings('h2')
#                             for h2_tag in h2_tags:
#                                 h2_title = h2_tag.text
#                                 h2_link = f'#'
#                                 h1_contents.append({'title': h2_title, 'link': h2_link})

#                             # Append the h1 title and its related h2 tags to the table of contents
#                             table_of_contents.append({'title': h1_title, 'link': h1_link, })
                            
#                         # Find all standalone h2 tags
#                         h2_tags = soup.find_all('h2')
#                         for h2_tag in h2_tags:
#                             h2_title = h2_tag.text
#                             h2_link = f'#'
#                             table_of_contents.append({'title': h2_title, 'link': h2_link, })
                
#                 # Save table of contents data to the database
#                 for toc_data in table_of_contents:
#                     TableofContentModel.objects.create(
#                         post=post,
#                         title=toc_data['title'],
#                         link=toc_data['link']
#                 )

#                 response_data = {
#                     'post_id': post_id,
#                     'category': category,
#                     'post_title': post_title,
#                     "post_url": post.post_url,
#                     'feature_image': feature_image,
#                     'post_content_with_media': final_content,
#                     'table_of_contents': table_of_contents,
#                     'related_posts': realated_post_data
#                 }
                
#                 return Response(response_data)
            
#             except PostModel.DoesNotExist:
#                 return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
            
            


class PostFetchView(WatchDogMixin, generics.RetrieveAPIView):

    def get_serializer(self, *args, **kwargs):
        return None

    queryset = PostModel.objects.all()
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('pk')
            post = self.queryset.get(id=post_id)
            self.generate_table_of_contents(post)
            table_of_contents = TableofContentModel.objects.filter(post=post)
            table_of_contents_data = [{'id': toc.id, 'title': toc.title, 'link': toc.link, 'status': toc.activated} for toc in table_of_contents]
            response_data = {
                'post_id': post_id,
                'category': post.category.category,
                'post_title': post.title,
                "post_url": post.post_url,
                'feature_image': request.build_absolute_uri(post.feature_image.url) if post.feature_image else None,
                'post_content_with_media': self.generate_final_content(post),
                'table_of_contents': table_of_contents_data,
                'related_posts': self.get_related_posts(post)
            }

            return Response(response_data)

        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def generate_table_of_contents(self, post):
       
        final_content = self.generate_final_content(post)
        toc_data = []

        for content in final_content:
            soup = BeautifulSoup(content, 'html.parser')
            h1_tags = soup.find_all('h1')
            for h1_tag in h1_tags:
                h1_title = h1_tag.text
                h1_link = f'#'
                h1_contents = []

               
                h2_tags = h1_tag.find_next_siblings('h2')
                for h2_tag in h2_tags:
                    h2_title = h2_tag.text
                    h2_link = f'#'
                    h1_contents.append({'title': h2_title, 'link': h2_link})

               
                toc_data.append({'title': h1_title, 'link': h1_link})
                
          
            h2_tags = soup.find_all('h2')
            for h2_tag in h2_tags:
                h2_title = h2_tag.text
                h2_link = f'#'
                toc_data.append({'title': h2_title, 'link': h2_link})
                
       
        for toc_entry in toc_data:
            TableofContentModel.objects.create(
                post=post,
                title=toc_entry['title'],
                link=toc_entry['link']
            )

        return toc_data

    def generate_final_content(self, post):
        content_with_media = []
        post_content_items = PostContentModel.objects.filter(post=post)
        for content in post_content_items:
            media_data = {
                'content': content.content,
                'image': content.image.url if content.image else None,
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
  
  
class TableofContentFetchUpdateView(WatchDogMixin,generics.ListAPIView, generics.UpdateAPIView):
    lookup_field = 'post_id'
    
    def get_serializer(self, *args, **kwargs):
        return None
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('post_id')
            post = PostModel.objects.get(id=post_id)
            table_of_contents = TableofContentModel.objects.filter(post=post)
            table_of_contents_data = [{'id': toc.id, 'title': toc.title, 'link': toc.link, 'status': toc.activated} for toc in table_of_contents]
            return Response(table_of_contents_data)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('post_id')
            updates = request.data.get('updates')
            print(f"updates: {updates}")
            for update in updates:
                toc_id = update.get('id')
                status = update.get('status')
                if toc_id is not None and status is not None:
                    TableofContentModel.objects.filter(id=toc_id, post__id=post_id).update(activated=status)
                else:
                    return Response({"error": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"success": "Status updated for selected table of content items"}, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class TableofContentUpdateView(WatchDogMixin, generics.RetrieveUpdateDestroyAPIView):
    
    def get_serializer(self, *args, **kwargs):
        return None
    
    queryset = TableofContentModel.objects.all()
    lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            toc_id = self.kwargs.get('pk')
            toc = self.queryset.get(id=toc_id)
            toc_data = {'id':toc.id,'title': toc.title, 'link': toc.link, 'status':toc.activated}
            return Response(toc_data)
        except TableofContentModel.DoesNotExist:
            return Response({"error": "Table of content not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            toc_id = self.kwargs.get('pk')
            toc = self.queryset.get(id=toc_id)
            toc.activated = request.data.get('status')
            toc.save()
            return Response({'message': 'Table of content updated successfully'})
        except TableofContentModel.DoesNotExist:
            return Response({"error": "Table of content not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
       # delete are not allowed
        return Response({"status": False, "msg": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        

class TableofContentActivateView(WatchDogMixin, generics.RetrieveAPIView):
    
    def get_serializer(self, *args, **kwargs):
        return None
    
    lookup_field = 'post_id'
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('post_id')
            post = PostModel.objects.get(id=post_id)
            table_of_contents = TableofContentModel.objects.filter(post=post, activated=True)
            table_of_contents_data = [{'id': toc.id, 'title': toc.title, 'link': toc.link, 'status': toc.activated} for toc in table_of_contents]
            return Response(table_of_contents_data) 
        except TableofContentModel.DoesNotExist:
            return Response({"error": "Table of content not found"}, status=status.HTTP_404_NOT_FOUND)
        
    