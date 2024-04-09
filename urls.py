# urls.py
from django.urls import path
from Blog.views.post_create_views import *
from Blog.views.post_fetching_views import *
from Blog.views.subscriptions_views import *
from Blog.views.external_post_create_views import *
from Blog.views.post_files_download_views import *
from Blog.views.clients_site_post_search_views import *
from Blog.views.table_of_content_views import *



urlpatterns = [
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    # path('posts/details/list/', PostDetailsListView.as_view(), name='post-details-list'),
    path ('posts/list/', PostListView.as_view(), name='post-list'),
    path('posts/update/<int:pk>/', PostUpdateView.as_view(), name='post-update'),
    path('posts/total/viwer/<int:pk>/', TotalViewerCountView.as_view(), name='total-viewer-count'),
    path('posts/views/with/tableofcontent/<int:pk>/', PostViewWithTableofContentView.as_view(), name='post-view-with-tableofcontent'),
    
    #download post content
    path('post/download/<int:post_id>/', DownloadPostContentView.as_view(), name='post-download'),
  
    
    # add view for post content
    path('post/add/viewer/<str:post_url>/', PostContentView.as_view(), name='post-content-view'),

    
    # ADD BLOG CATEGORY URLS HERE 
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    path('category/details/list/', CategoryDetailsListView.as_view(), name='category-details-list'),
    path('category/details/update/<int:pk>/', CategoryUpdateView.as_view(), name='category-details-update'),
    
    
    #site urls add
    path('site/name/create/', SiteCreateView.as_view(), name='site-create'),
    path('site/name/list/', SiteListView.as_view(), name='site-list'),
    path('site/name/update/<int:pk>/', SiteUpdateView.as_view(), name='site-update'),
    
    # external published post urls
    path('external/post/create/', ExternalPostCreateView.as_view(), name='external-post-create'),
    path('external/post/list/', ExternalPostListView.as_view(), name='external-post-list'),
    path ('external/post/update/<int:pk>/', ExternalPostDetailView.as_view(), name='external-post-update'),
    path ('external/post/viewer/<int:pk>/', ExternalPostViewerCountView.as_view(), name='external-post-viewer'),
    
    #subscription urls
    path('subscription/create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('subscription/list/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscription/unsubscribe/<int:pk>/', SubscriptionUnsubscribeView.as_view(), name='subscription-unsubscribe'),
    
    
    #view for post content in client side
    path('post/all/views/', PostAllView.as_view(), name='post-all'),
    path('post/categorywise/views/', PostCategoryWiseView.as_view(), name='post-categorywise'),
    
    path('post/fetch/<int:pk>/', PostFetchView.as_view(), name='post-fetch'),
    path('post/tableofcontent/fetch/<int:post_id>/', TableofContentFetchUpdateView.as_view(), name='tableofcontent-fetch'),
    path('post/tableofcontent/update/<int:pk>/', TableofContentUpdateView.as_view(), name='tableofcontent-update'),
    path('post/tableofcontent/activate/<int:post_id>/', TableofContentActivateView.as_view(), name='tableofcontent-activate'),
    path('post/global/search/', PostGlobalSearchView.as_view(), name='post-global-search'),
    
]