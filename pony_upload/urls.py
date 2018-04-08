from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_upload, name="initiate"),
    path('upload-part/', views.upload_part, name="upload-part"),
    path('complete-upload/', views.complete_upload, name="complete-upload"),
    path('abort-upload/', views.abort_upload, name="abort-upload"),
    path('list-parts/', views.list_parts, name="list-parts"),
    path('list-uploads/', views.list_uploads, name="list-uploads"),
]
