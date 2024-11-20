from django.urls import path
from . import views

urlpatterns = [
    path('extract-text-from-video', views.change_video_to_text_content, name='change_video_to_text_content'),
    path('extract-audio-from-video', views.extract_audio_from_video, name='extract-audio-from-video'),
    path('download-youtube-video', views.download_youtube_video, name='download_youtube_video'),
    path('download-youtube-audio', views.download_youtube_audio, name='download_youtube_audio'),
    path('download-instagram-video', views.download_instagram_video, name='download_instagram_video'),   
    path('download-facebook-video', views.download_facebook_video, name='download_facebook_video'),   
    path('download-youtube-video-url', views.download_youtube_video_url, name='download_youtube_video_url'),       
]
