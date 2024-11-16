from django.urls import path
from . import views

urlpatterns = [
    path('extract-text-from-video', views.change_video_to_text_content, name='change_video_to_text_content'),
    path('extract-audio-from-video', views.extract_audio_from_video, name='extract-audio-from-video'),
]
