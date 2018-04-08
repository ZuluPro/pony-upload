from django.urls import path, include

urlpatterns = [
    path('', include('pony_upload.urls')),
]
