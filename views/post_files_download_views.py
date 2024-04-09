import os
from rest_framework import generics, status
from rest_framework.response import Response

import zipfile
from django.conf import settings
from Blog.models import *
from AuthGuard.utils import WatchDogMixin
from django.http import HttpResponse
from googleapiclient.discovery import build

class DownloadPostContentView(WatchDogMixin,generics.RetrieveAPIView):
    def get_serializer(self, *args, **kwargs):
        return None

    lookup_field = 'post_id'


    def get(self, request, *args, **kwargs):
        try:
          
            self.get_authenticated_user()

           
            post_id = self.kwargs.get('post_id')

          
            post_content = PostContentModel.objects.filter(post_id=post_id)

            temp_dir = os.path.join(settings.BASE_DIR, 'temp_download')
            os.makedirs(temp_dir, exist_ok=True)

         
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            content_file_names = set()

        
            zip_file_path = os.path.join(temp_dir, f'post_{post_id}.zip')
            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                for content_item in post_content:
                  
                    content_file_name = f'content_{content_item.id}.html'
                    if content_file_name not in content_file_names:
                        try:
                            content_data = content_item.content.encode('utf-8')  # Try to encode as UTF-8
                        except UnicodeEncodeError:
                            content_data = content_item.content.encode('latin-1')  # Fallback to latin-1 encoding
                        zip_file.writestr(content_file_name, content_data)

                        
                        content_file_names.add(content_file_name)
                    
                    if content_item.image:
                        zip_file.write(content_item.image.path, arcname=os.path.basename(content_item.image.path))
                    if content_item.video:
                        zip_file.writestr(f'video_{content_item.id}.txt', content_item.video)

          
            with open(zip_file_path, 'rb') as zip_file:
                response =HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename=post_{post_id}.zip'

            return response

        except PostContentModel.DoesNotExist:
            return Response({"error": "Post content not found"}, status=status.HTTP_404_NOT_FOUND)




def upload_video(request):
        # Initialize the YouTube API client
        youtube = build('youtube', 'v3', developerKey='AIzaSyDiwlTq2SjQkLLGs-2PpS6LmzYupRWGck8')

        # Prepare video metadata
        request_body = {
            'snippet': {
                'title': 'My Uploaded Video',
                'description': 'Description of my video',
                # Add more metadata as needed
            },
            'status': {
                'privacyStatus': 'public',  
            }
        }

        # Upload video
        insert_request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=request.FILES['video_file'] 
        )
        response = insert_request.execute()

        # Extract video URL
        video_url = f"https://www.youtube.com/watch?v={response['id']}"

        # Save video URL to the database PostContentModel
        PostContentModel.objects.create(video=video_url)
        
        return Response({"video_url": video_url}, status=status.HTTP_201_CREATED)
    
         
