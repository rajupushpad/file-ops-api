from django.urls import path
from . import views

urlpatterns = [
    path('extract-text-from-video', views.change_video_to_text_content, name='change_video_to_text_content'),
    path('extract-audio-from-video', views.extract_audio_from_video, name='extract-audio-from-video'),
    path('download-youtube-video-url', views.download_youtube_video_url, name='download_youtube_video_url'),     
    path('download-instagram-video-url', views.download_instagram_video_url, name='download_instagram_video_url'),   
    path('download-facebook-video-url', views.download_facebook_video_url, name='download_facebook_video_url'),     
]