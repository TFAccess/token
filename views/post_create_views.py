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
from django.shortcuts import get_object_or_404
import base64
from uuid import uuid4
import json
import subprocess
# custom pagination
from ServiceHub.utils.custom_pagination_util import CustomPagination
from googleapiclient.discovery import build
from django.contrib.sites.shortcuts import get_current_site
from googleapiclient.http import MediaIoBaseUpload
from Blog.utils import get_credentials



class PostCreateView(WatchDogMixin, generics.CreateAPIView):
    
    serializer_class = PostSerializer
    
        
    def create(self, request, *args, **kwargs):
            try:
                
                self.get_authenticated_user()
                featured_image = request.data.get('feature_image')
                content_data = request.data.get('post_content', [])
                posted_sites = request.data.get('posted_sites', [])
                keywords = request.data.get('keywords', [])
                category = request.data.get('category')
                sub_category = request.data.get('sub_categories')
                filter_option= request.data.get('filter_option')
               
          
                if featured_image:
                    format, imgstr = featured_image.split(';base64,') 
                    file_name = format.split('/')[-1] 
                    data = ContentFile(base64.b64decode(imgstr), name='temp.' + file_name)
                    request.data['feature_image'] = data
                request.data['category'] = category
                request.data['sub_categories'] = sub_category
                request.data['filter_option'] = filter_option
                request.data['author'] = self.get_authenticated_user().id
                serializer = self.get_serializer(data=request.data)
                print(f"contendddddt_data: {content_data}")
                serializer.is_valid(raise_exception=True)
                post = serializer.save()
                print(f"last content_data: {content_data}")
                # Check if post is None
                if post is None:
                    raise ValueError("Failed to create the post")

                # Print the post object for debugging
                print("Post created:", post)
                post_content_instances = []
                
                for content_item in content_data:
                    image_base64 = content_item.get('image')
                    video_base64 = content_item.get('video')
                    
                    if image_base64:
                        try:
                            format, imgstr = image_base64.split(';base64,')
                            ext = format.split('/')[-1]
                            unique_filename = f"{uuid4()}.{ext}"
                            data = ContentFile(base64.b64decode(imgstr), name=unique_filename)
                            content_item['image'] = data
                        except Exception as e:
                            print(f"Error processing image: {e}")
                            continue
                    elif video_base64:
                                # command = [
                                #     "python",  # Path to Python executable
                                #     "upload_video.py",  # Path to the upload_video.py script
                                #     f"--file={video_base64}",  # Pass the video base64 data as file
                                #     "--title=Your video title",
                                #     "--description=Your video description",
                                #     "--keywords=comma,separated,keywords",
                                #     "--category=22",  # Video category ID
                                #     "--privacyStatus=private"  # Privacy status of the video
                                # ]
                                
                                # # Execute the command
                                # result = subprocess.run(command, capture_output=True, text=True)

                                # # Check if the command was successful
                                # if result.returncode == 0:
                                #     print("Video uploaded successfully.")
                                # else:
                                #     print("Error uploading video:", result.stderr)
                        try:
                            credentials = get_credentials()
                            if ';base64,' in video_base64:
                                format, vidstr = video_base64.split(';base64,')
                                ext = format.split('/')[-1]
                                unique_filename = f"{uuid4()}.{ext}"
                                data = base64.b64decode(vidstr)
                                
                                # Upload video to YouTube
                                youtube = build('youtube', 'v3', developerKey='AIzaSyDiwlTq2SjQkLLGs-2PpS6LmzYupRWGck8')
                                request_body = {
                                    'snippet': {
                                        'title': 'Uploaded Video Title',
                                        'description': 'Description of the uploaded video',
                                    },
                                    'status': {
                                        'privacyStatus': 'public',
                                    }
                                }
                                media = MediaIoBaseUpload(ContentFile(data, name=unique_filename), mimetype='video/*')
                                insert_request = youtube.videos().insert(
                                    part='snippet,status',
                                    body=request_body,
                                    media_body=media
                                )
                                response = insert_request.execute()
                                youtube_video_id = response['id']
                                
                                # Store YouTube video ID in your database
                                content_item['video'] = f"https://www.youtube.com/watch?v={youtube_video_id}"
                            else:
                                raise ValueError("Invalid video_base64 format: missing ';base64,' delimiter")
                        except Exception as e:
                            print(f"Error processing video: {e}")
                            continue
                        
                       
                    content_item['post'] = post
                    post_content_instance = PostContentModel.objects.create(**content_item)
                    post_content_instances.append(post_content_instance)
                    
                post.post_content.set(post_content_instances)
                                
                for site_id in posted_sites:
                    site = PostedSiteModel.objects.get(id=site_id)
                    post.posted_sites.add(site)

                post.keywords = keywords
                post.save()

                # Return the response data with post id
                return Response({"status": True, "msg": "Post Created Successfully.", "post_id": post.id}, status=status.HTTP_201_CREATED)
               
            
            except Exception as e:
                return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class PostDetailsListView(WatchDogMixin, generics.CreateAPIView):
    
#     serializer_class = databackupSerializer
    
#     def perform_create(self, serializer):
        
#         author = self.request.user
#         auther_id = author.id
#         # fetch user name from user model acci=oding to id
#         author = User.objects.get(id=auther_id)
#         author_name = author.full_name
#         post_title = serializer.validated_data.get('title')
#         category_name = serializer.validated_data.get('category').category
#         short_description = serializer.validated_data.get('short_description')
#         posted_sites = serializer.validated_data.get('posted_sites')
#         updated_date = serializer.validated_data.get('updated_date')
#         image = serializer.validated_data.get('feature_image')
#         post_url = serializer.validated_data.get('post_url')

#         schema_data = {
#             "@context": "http://schema.org",
#             "@type": category_name,
#             "headline": post_title,
#             "description": short_description,
#             "datePublished": updated_date,
#             "dateModified": updated_date,
#             "author": {
#                 "@type": "Person",
#                 "name": author_name,
#             },
#             "image": {},
#             "publisher": {},
#             "mainEntityOfPage": {
#                 "@type": "WebPage",
#                 "@id": post_url,
#             }
#         }

#         if image:
#             schema_data["image"] = {
#                 "@type": "ImageObject",
#                 "url": image.url,
#                 "height": 800,
#                 "width": 1200
#             }

#         for site in posted_sites:
#             publisher_data = {
#                 "@type": "Organization",
#                 "name": site.posted_site,
#             }
#             if site.site_logo and site.site_logo.url:
#                 publisher_data["logo"] = {
#                     "@type": "ImageObject",
#                     "url": site.site_logo.url,
#                 }
#             schema_data["publisher"] = publisher_data

#         serializer.save(author=author, schema_data=schema_data)
        
        
#     def post(self, request, *args, **kwargs):
#         try:
#             self.get_authenticated_user()
#             return super().post(request, *args, **kwargs)
#         except Exception as e:
#             return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class PostListView(WatchDogMixin, generics.ListAPIView):
    pagination_class = CustomPagination

    def get_serializer(self, *args, **kwargs):
        return None
    
    def get_queryset(self):
        # Retrieve the query parameters from the request
        category = self.request.query_params.get('category', '') 
        sub_category = self.request.query_params.get('sub_category', '')
        posted_site = self.request.query_params.get('posted_site', '')
        
        quick_search = self.request.query_params.get('quick_search') or None  # New: Get search query
    
        if quick_search:
           
            # Filter the queryset based on the query parameters
            queryset = PostModel.objects.filter(
                Q(title__icontains=quick_search) | Q(short_description__icontains=quick_search) |
                Q(category__category__icontains=quick_search) | Q(sub_categories__sub_category__icontains=quick_search) |
                Q(posted_sites__posted_site__icontains=quick_search)
            )
            return queryset.distinct().order_by('-date')
        
        # Filter the queryset based on the query parameters
        queryset = PostModel.objects.filter(category__category__icontains=category,
                                            sub_categories__sub_category__icontains=sub_category,
                                            posted_sites__posted_site__icontains=posted_site)
        
        
        print(f"queryset: {queryset}")
        return queryset.distinct().order_by('-date')
        
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            
            # Get the paginated queryset
            queryset = self.paginate_queryset(self.get_queryset())
            data = []
            for post in queryset:
                site_names_list = post.posted_sites.all().values_list('posted_site', flat=True)
                post_data = {
                    "post_id": post.id,
                    "post_name": post.title,
                    "post_category": post.category.category,
                    "post_sub_category": post.sub_categories.sub_category if post.sub_categories else "No Subcategory",
                    "post_url": post.post_url,
                    "published_sites": site_names_list, 
                    "post_date": post.date,
                    "total_views": post.total_view,
                }
                data.append(post_data)
            return self.get_paginated_response(data)
        
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostAllView(WatchDogMixin, generics.ListAPIView):
      
    
    def get_serializer(self, *args, **kwargs):
        return None  
        
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            
            # Retrieve query parameters from the request
            category = request.query_params.get('category', '')
            sub_category = request.query_params.get('sub_category', '')
            posted_site = request.query_params.get('posted_site', '')
            search_query = request.query_params.get('q', '')  # New: Get search query
            
            # Filter posts based on query parameters
            posts = PostModel.objects.filter(
                Q(category__category__icontains=category) &
                Q(sub_categories__sub_category__icontains=sub_category) &
                Q(posted_sites__posted_site__icontains=posted_site) &
                (Q(title__icontains=search_query) | Q(short_description__icontains=search_query))  # New: Search query
            )
            
            # Fetch most popular posts (most viewed)
            most_popular_posts = posts.annotate(total_views=Count('total_view')).order_by('-total_views')[:5]
            
            # Fetch recent articles
            recent_articles = posts.order_by('-updated_date')[:5]
            
            # Group posts by category and sub-category
            grouped_posts = {}
            for post in posts:
                category_name = post.category.category if post.category else "Uncategorized"
                if category_name not in grouped_posts:
                    grouped_posts[category_name] = []
                grouped_posts[category_name].append({
                    "post_image": post.feature_image.url if post.feature_image else "",  # Assuming feature_image is an ImageField
                    "description": post.short_description,
                    "uploaded_date": post.date.strftime("%d/%m/%Y")  # Adjust date format as needed
                })
            
            # Prepare the response data
            data = {
                "status": True,
                "data": [
                    {"category": list(grouped_posts.keys())},
                    {"Most Popular Post": [
                        {
                            "post_image": post.feature_image.url if post.feature_image else "",
                            "description": post.short_description,
                            "uploaded_date": post.date.strftime("%d/%m/%Y")
                        } for post in most_popular_posts
                    ]},

                    {category_name: grouped_posts[category_name] for category_name in grouped_posts},
                    
                    {"Most recent Aricles": [
                        {
                            "post_tittle": post.title,
                            "update_date": post.updated_date.strftime("%d/%m/%Y")
                        } for post in recent_articles
                    ]}
                ]
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostCategoryWiseView(WatchDogMixin, generics.ListAPIView):
    
    
    def get_serializer(self, *args, **kwargs):
        return None
  
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            
            category = request.query_params.get('category', '')
            sub_category = request.query_params.get('sub_category', '')
            posted_site = request.query_params.get('posted_site', '')
            search_query = request.query_params.get('q', '') 
            
            posts = PostModel.objects.filter(
                Q(category__category__icontains=category) &
                Q(sub_categories__sub_category__icontains=sub_category) &
                Q(posted_sites__posted_site__icontains=posted_site) &
                (Q(title__icontains=search_query) | Q(short_description__icontains=search_query))  
            )
            
            all_categories = PostModel.objects.values_list('category__category', flat=True).distinct()
            
            # Fetch most popular posts (most viewed) in the selected category
            most_popular_posts = posts.annotate(total_views=Count('total_view')).order_by('-total_views')[:5]
            
            # Fetch subcategories related to the selected category
            subcategories_posts = {}
            for post in posts:
                sub_category_name = post.sub_categories.sub_category if post.sub_categories else "No Subcategory"
                if sub_category_name not in subcategories_posts:
                    subcategories_posts[sub_category_name] = []
                if len(subcategories_posts[sub_category_name]) < 5:
                    subcategories_posts[sub_category_name].append({
                        "post_id": post.id,  
                        "post_url": post.post_url,  
                        "post_image": post.feature_image.url if post.feature_image else "",  
                        "post_title": post.title,
                        "uploaded_date": post.date.strftime("%d/%m/%Y")
                    })
            
            # Fetch recent articles related to the selected category
            recent_articles = posts.order_by('-updated_date')[:5]
            
            # Prepare the response data
            all_posts = PostModel.objects.all()
            
            
            data = {
                "status": True,
                "all_post": [
                    {"post_id": post.id, "post_url": post.post_url} for post in all_posts
                ],
                "data": [
                    {"All Categories": list(all_categories)},
                    {"Most Popular Post": [
                        {    "post_id": post.id,
                            "post_url": post.post_url,
                            "post_image": post.feature_image.url if post.feature_image else "",
                            "post_title": post.title,
                            "uploaded_date": post.date.strftime("%d/%m/%Y")
                        } for post in most_popular_posts
                    ]},
                    {"Subcategories Posts": [
                        {"subcategory": sub_category_name, "posts": subcategories_posts[sub_category_name]}
                        for sub_category_name in subcategories_posts
                    ]},
                    {"Most Recent Post": [
                        {   "post_id": post.id,
                            "post_url": post.post_url,
                            "post_tittle": post.title,
                            "update_date": post.updated_date.strftime("%d/%m/%Y")
                        } for post in recent_articles
                    ]}
                ]
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
                
class CategoryDetailsListView(WatchDogMixin, generics.ListAPIView):
    
    
    def get_serializer(self, *args, **kwargs):
        return None
        
    def get(self, request, *args, **kwargs):
        
        try:
            self.get_authenticated_user()
                    
            categories = BlogCategoryModel.objects.all()

            data = []
            for category in categories:
                subcategories = BlogSubCategoryModel.objects.filter(category=category)
                subcategory_count = subcategories.count()
                subcategory_data = [{ "id":subcategory.id,"name": subcategory.sub_category} for subcategory in subcategories]

                total_post_count = 0
                for subcategory in subcategories:
                    post_count = PostModel.objects.filter(category=category, sub_categories=subcategory).count()
                    total_post_count += post_count

                total_views = PostModel.objects.filter(category=category).aggregate(total_views=Sum('total_view'))['total_views'] or 0

                category_info = {
                    "id": category.id,
                    "category": category.category,
                    "subcategories": subcategory_data,
                    "total_subcategories": subcategory_count,
                    "total_post": total_post_count,
                    "total_views": total_views
                }
                data.append(category_info)

            response_data = {
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class CategoryUpdateView (WatchDogMixin, generics.RetrieveUpdateDestroyAPIView):
        
        serializer_class = BlogCategorySerializer
        queryset = BlogCategoryModel.objects.all()
        lookup_field = 'pk'
        
        def update(self, request, *args, **kwargs):
            try:
                self.get_authenticated_user()
                return super().update(request, *args, **kwargs)
            except Exception as e:
                return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        def get(self, request, *args, **kwargs):
            try:
                self.get_authenticated_user()
                return super().get(request, *args, **kwargs)
            except Exception as e:
                return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        def destroy(self, request, *args, **kwargs):
        # delete are not allowed
            return Response({"status": False, "msg": "Delete operation not allowed."}, status=status.HTTP_400_BAD_REQUEST)
class PostUpdateView(WatchDogMixin, generics.RetrieveUpdateDestroyAPIView):
    
    
    pagination_class = CustomPagination
    
    serializer_class = PostSerializer
    queryset = PostModel.objects.all()
    lookup_field = 'pk'
    
    def base64_to_file(self, base64_data, filename):
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]  
            unique_filename = f"{uuid4()}.{ext}"  
            return ContentFile(base64.b64decode(imgstr), name=unique_filename)
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
        
        
    def update(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            title = request.data.get('title')
            featured_image = request.data.get('feature_image')
            content_data = request.data.get('post_content', [])
            posted_sites = request.data.get('posted_sites', [])
            keywords = request.data.get('keywords', [])
            category = request.data.get('category')
            sub_category = request.data.get('sub_categories')
            filter_option = request.data.get('filter_option')
            
            # Handle featured image
            if featured_image and featured_image.startswith('data:image'):
                format, imgstr = featured_image.split(';base64,') 
                file_name = format.split('/')[-1] 
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + file_name)
                request.data['feature_image'] = data
            else:
                request.data['feature_image'] = instance.feature_image
                    
            request.data['category'] = category
            request.data['sub_categories'] = sub_category
            request.data['filter_option'] = filter_option
            request.data['author'] = self.get_authenticated_user().id
            
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            post = serializer.save()
            
            # Get existing content items
            existing_content_items = instance.post_content.all()
            existing_content_item_ids = set(existing_content_items.values_list('id', flat=True))
            
            # Update or create new content items
            updated_content_item_ids = []
            for content_item in content_data:
                content_item_id = content_item.get('id')
                if content_item_id:
                    updated_content_item_ids.append(content_item_id)
                    
                    
                if content_item_id in existing_content_item_ids:
                    # Update existing content item
                    existing_item = existing_content_items.get(id=content_item_id)
                    existing_item.content = content_item.get('content', existing_item.content)
                    existing_item.image = content_item.get('image', existing_item.image)
                    existing_item.video = content_item.get('video', existing_item.video)
                    existing_item.alignment = content_item.get('alignment', existing_item.alignment)
                    existing_item.padding_top = content_item.get('padding_top', existing_item.padding_top)
                    existing_item.padding_bottom = content_item.get('padding_bottom', existing_item.padding_bottom)
                    existing_item.padding_left = content_item.get('padding_left', existing_item.padding_left)
                    existing_item.padding_right = content_item.get('padding_right', existing_item.padding_right)
                    existing_item.tracking = content_item.get('tracking', existing_item.tracking)
                    existing_item.save()
                else:
                    # image_base64 = content_item.get('image')
                    
                    image_base64 = content_item.get('image')
                    if image_base64:
                        data = self.base64_to_file(image_base64, 'image')
                        if data:
                            content_item['image'] = data
                        else:
                            pass
                            
                    content_item['post'] = post
                    PostContentModel.objects.create(**content_item)
            
            # Delete content items not included in the updated payload
            deleted_content_item_ids = existing_content_item_ids - set(updated_content_item_ids)
            for content_item_id in deleted_content_item_ids:
                existing_content_items.get(id=content_item_id).delete()
                
            
            
            # Add posted sites
            for site_id in posted_sites:
                site = PostedSiteModel.objects.get(id=site_id)
                post.posted_sites.add(site)

            post.keywords = keywords
            post.save()
            # remove previous all table of content
            table_of_content = TableofContentModel.objects.filter(post=post)
            print(f"table_of_content: {table_of_content}")
            if table_of_content:
                table_of_content.delete()
           
            # Return the response data
            return Response({"status": True, "msg": "Post Updated Successfully.","post_id":post.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        
     
     
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            # fetch post content from postcontentmodel 
            post_id = self.kwargs.get('pk')
            post = PostModel.objects.get(id=post_id)
            post_content = PostContentModel.objects.filter(post=post)
            current_site = get_current_site(request)
            #take doamin
            domain = current_site.domain
            post_content_data = []
            for content in post_content:
                post_content_data.append({
                    "id": content.id,
                    "content": content.content,
                    "image": request.build_absolute_uri(content.image.url) if content.image else "",
                    "video": content.video,
                    "alignment": content.alignment,
                    "padding_top": content.padding_top,
                    "padding_bottom": content.padding_bottom,
                    "padding_left": content.padding_left,
                    "padding_right": content.padding_right,
                    "tracking": content.tracking
                    
                    
                })
            data = {
                "post_id": post.id,
                "post_name": post.title,
                "post_category": post.category.category,
                "post_sub_category": post.sub_categories.sub_category if post.sub_categories else "No Subcategory",
                "post_url": post.post_url,
                "feature_image": request.build_absolute_uri(post.feature_image.url) if post.feature_image else "",
                "feature_image_title": post.feature_image_title,
                "feature_image_alt_text": post.feature_image_alt_text,
                "short_description": post.short_description,
                "post_content": post_content_data,
                "posted_sites": post.posted_sites.all().values_list('id', flat=True),
                "total_views": post.total_view,
                "comment_option": post.comment_option,
                "keywords": post.keywords,
            }
            return Response({"status": True, "data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"status": True, "msg": "Object deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TotalViewerCountView(WatchDogMixin, generics.RetrieveAPIView):
    
    serializer_class = PostSerializer
    queryset = PostModel.objects.all()
    lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_id = self.kwargs.get('pk')
            total_viewer = PostModel.objects.filter(id=post_id).aggregate(Sum('total_viewer'))
            return Response({"status": True, "total_viewer": total_viewer['total_viewer__sum']}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class PostContentView(WatchDogMixin, generics.RetrieveAPIView):
    
    def get_serializer(self, *args, **kwargs):
        return None
    
    
    # get post url her 
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            post_url = self.kwargs.get('post_url')
            print(f"post_url: {post_url}")
            post = PostModel.objects.get(post_url=post_url)
            # update total view in  this view
            post.total_view += 1
            post.save()
            return Response({"status": True, "msg": "Total view updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    
    
    
  


class CategoryCreateView(WatchDogMixin, CreateAPIView):
    serializer_class = BlogCategorySerializer

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class SiteCreateView(WatchDogMixin, CreateAPIView):
    
    
    serializer_class = SiteNamecreateSerializer
    
    def base64_to_file(self, base64_data, filename):
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            unique_filename = f"{uuid4()}.{ext}"
            return ContentFile(base64.b64decode(imgstr), name=unique_filename)
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def post(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            request.data['site_logo'] = self.base64_to_file(request.data.get('site_logo'), 'logo')
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class SiteListView(WatchDogMixin, generics.ListAPIView): 
    
    serializer_class = SiteNameSerializer
    queryset = PostedSiteModel.objects.all()
    pagination_class = CustomPagination
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            queryset = self.get_queryset()
            serializer = SiteNameSerializer(queryset, many=True, context={'request': request})
            page = self.paginate_queryset(serializer.data)
            Pagination = self.get_paginated_response(page).data
            # add posted site id
            for data in Pagination['results']:
                data['id'] = self.queryset.get(posted_site=data['posted_site']).id
                
            return Response({"status": True, "data": Pagination}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class SiteUpdateView(WatchDogMixin, generics.RetrieveUpdateDestroyAPIView):
    
    
    serializer_class = SiteNamecreateSerializer
    queryset = PostedSiteModel.objects.all()
    
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        
        try:
            self.get_authenticated_user()
            intense = self.get_object()
            image_data = request.data.get('site_logo')
            # if site logo start with data:image
            if image_data and image_data.startswith('data:image'):
                
                format, imgstr = request.data['site_logo'].split(';base64,')
                ext = format.split('/')[-1]
                unique_filename = f"{uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=unique_filename)
                request.data['site_logo'] = data
                
            # if site logo is null it can be updated with empty
            elif image_data == 'null':
                request.data['site_logo'] = None
            else:
                request.data['site_logo'] = intense.site_logo
            return super().update(request, *args, **kwargs)
                
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request, *args, **kwargs):
        try:
            self.get_authenticated_user()
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"status": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
    def destroy(self, request, *args, **kwargs):
         # delete method not allowed
        return Response({"status": False, "msg": "Delete method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
            
            
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
        