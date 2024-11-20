from urllib import response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.http import FileResponse

import moviepy.editor as mp 
import speech_recognition as sr 
import os

import yt_dlp
import random
import re
from yt_dlp import YoutubeDL

@api_view(['POST'])
def change_video_to_text_content(request):

    uploaded_file = request.FILES['file']

    try: 
        # Save the uploaded file to a temporary location
        temp_file_path = default_storage.save('temp_video.mp4', ContentFile(uploaded_file.read()));
        resText="";

        if temp_file_path:
            resText = extractTextFromVideoFile('media/'+temp_file_path, "hi-IN")
            print(resText)


        # return Response({'message': 'File converted successfully'})
        return Response({'message': 'Conversion successful', 'resText': resText}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': 'Conversion failed', 'resText': ""}, status=500)

    finally:
        # Clean up the temporary file
        if temp_file_path:
            full_temp_path = os.path.join(default_storage.location, temp_file_path)
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)


def extractTextFromVideoFile(file, textLang="en-US"):

    try:
        finalText = ""

        # Load the video 
        video = mp.VideoFileClip(file) 
        # video = mp.VideoFileClip("https://www.youtube.com/watch?v=k6WmiOhFCdY") 

        # Set the start and end times for the 1-minute clip
        start_time = 0  # Start time in seconds
        end_time = 60   # End time in seconds (1 minute)
        iteration = 0;

        while end_time < video.duration or (video.duration  < 60 and iteration == 0):
            
            if end_time > video.duration:
                end_time = video.duration

            # Create the 1-minute clip
            video_clip = video.subclip(start_time, end_time)

            # Extract the audio from the clip
            audio_clip = video_clip.audio
            audio_clip.write_audiofile("res.wav")

            # Initialize recognizer
            r = sr.Recognizer()

            # Load the audio file
            with sr.AudioFile("res.wav") as source:
                data = r.record(source)

            # Convert speech to text
            text = r.recognize_google(data, language=textLang) 

            finalText = finalText + text 

            start_time = start_time + 61  # Start time in seconds
            end_time = end_time + 60


            if end_time > video.duration and start_time < end_time:
                end_time = video.duration
            
            iteration = iteration + 1;

        return finalText;

    except Exception as e:
        print(str(e))

@api_view(['POST'])
def extract_audio_from_video(request):
    uploaded_file = request.FILES['file']

    try:
        # Save the uploaded file to a temporary location
        temp_file_path = default_storage.save('temp_video.mp4', ContentFile(uploaded_file.read()));

        if temp_file_path:

            # Create a VideoFileClip from the temporary file
            
            video_clip = mp.VideoFileClip('media/'+temp_file_path)

            # Extract the audio from the video clip
            audio_clip = video_clip.audio

            # You can now use 'audio_clip' as needed

            output_audio_path = 'media/output_audio.mp3'

            # Save the audio clip to the local directory
            audio_clip.write_audiofile(output_audio_path)

            with open(output_audio_path, 'rb') as audio_file:
                response = HttpResponse(audio_file.read())
                response['Content-Type'] = 'audio/mpeg'
                response['Content-Disposition'] = 'attachment; filename="output_audio.mp3"'
                return response
    
    except Exception as e:
        return Response({'message': 'Conversion failed'}, status=500)

    finally:
        # Clean up temporary video and output audio files
        if temp_file_path:
            full_temp_video_path = os.path.join(default_storage.location, temp_file_path)
            if os.path.exists(full_temp_video_path):
                os.remove(full_temp_video_path)

        if output_audio_path and os.path.exists(output_audio_path):
            os.remove(output_audio_path)

@api_view(['POST'])
def download_youtube_audio(request):
    """
    API to download audio from YouTube Music.
    Accepts a POST request with the YouTube video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    youtube_url = request.data['url']

    # Validate URL
    YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    if not re.match(YOUTUBE_URL_REGEX, youtube_url):
        return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

    temp_audio_path = ""
    try:
        # Define download options
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best audio quality
            'extractaudio': True,       # Extract only audio
            'audioformat': 'mp3',       # Convert to MP3
            'outtmpl': '%(title)s.%(ext)s',  # Save audio with title as filename
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',  # Extract audio using FFmpeg
                    'preferredcodec': 'mp3',     # Convert to MP3
                    'preferredquality': '192',   # Set MP3 quality to 192kbps
                }
            ],
            'nocheckcertificate': True,  # Skip SSL certificate verification
            'compat_opts': ['no-certifi'],  # Use compatibility options for certifi
        }

        # Use yt-dlp to download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            temp_audio_path = f"{info_dict['title']}.mp3"

        # Send the audio file back as a response
        with open(temp_audio_path, 'rb') as audio_file:
            response = HttpResponse(audio_file, content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(temp_audio_path)}"'
            return response

    except Exception as e:
        # Log the exception for debugging
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        # Clean up temporary files
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@api_view(['POST'])
def download_youtube_video(request):
    """
    API to download YouTube video.
    Accepts a POST request with the YouTube video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    youtube_url = request.data['url']

    # Validate URL
    YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    if not re.match(YOUTUBE_URL_REGEX, youtube_url):
        return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

    temp_video_path = ""
    output_path = "media/"
    filename = ''
    outputFilePath = f'{output_path}/output{random.randint(1, 1000)}.mp4'

    try:
        # Define download options
        ydl_opts = {
            'format': 'best',  # Download the best quality video
            'outtmpl': outputFilePath,  # Save video in the specified path

            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',  # Ensure compatible format
                'preferedformat': 'mp4',  # Convert to MP4 if needed
            }],
            'nocheckcertificate': True,  # Skip SSL certificate verification
            'compat_opts': ['no-certifi'],  # Use compatibility options for certifi
        }

        # Use yt-dlp to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            temp_video_path = os.path.join(outputFilePath)

            video_title = info_dict.get('title', 'youtube_video')  # Extract title
            video_extension = info_dict.get('ext', 'mp4')  # Extract file extension (default to mp4)

            # Construct filename
            filename = f"{video_title}.{video_extension}"

        # Send the video file back as a response
        with open(temp_video_path, 'rb') as video_file:
            response = HttpResponse(video_file, content_type='video/mp4')
            response['content-disposition'] = f'attachment; filename="{filename}"'
            return response

    except Exception as e:
        # Log the exception for debugging
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        # Clean up temporary files
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)


@api_view(['POST'])
def download_instagram_video(request):
    """
    API to download Instagram video.
    Accepts a POST request with the Instagram video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    instagram_url = request.data['url']
    output_path = "media/"  # Directory to save downloaded videos

    # Validate Instagram URL (basic check)
    INSTAGRAM_URL_REGEX = r'(https?://)?(www\.)?instagram\.com/.+'
    if not re.match(INSTAGRAM_URL_REGEX, instagram_url):
        return Response({'error': 'Invalid Instagram URL'}, status=status.HTTP_400_BAD_REQUEST)

    temp_video_path = ""
    try:
        # Define yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best video+audio or best available
            'merge_output_format': 'mp4',  # Ensure output is in MP4 format
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save with title as filename
            'nocheckcertificate': True,  # Skip SSL certificate verification
        }

        # Use yt-dlp to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url, download=True)
            video_title = info_dict.get('title', 'instagram_video')
            temp_video_path = os.path.join(output_path, f"{video_title}.mp4")

        # Serve the video as a response
        with open(temp_video_path, 'rb') as video_file:
            response = HttpResponse(video_file, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(temp_video_path)}"'
            return response

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        # Clean up downloaded file
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)

@api_view(['POST'])
def download_facebook_video(request):
    """
    API to download Facebook video.
    Accepts a POST request with the Facebook video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    facebook_url = request.data['url']
    output_path = "media/"  # Directory to save downloaded videos
    os.makedirs(output_path, exist_ok=True)

    # Validate Facebook URL (basic check)
    FACEBOOK_URL_REGEX = r'(https?://)?(www\.)?(facebook\.com|fb\.watch)/.+'
    if not re.match(FACEBOOK_URL_REGEX, facebook_url):
        return Response({'error': 'Invalid Facebook URL'}, status=status.HTTP_400_BAD_REQUEST)

    temp_video_path = ""
    filename = '%(title)s.%(ext)s'
    outputFilePath = f'{output_path}/output{random.randint(1, 1000)}.mp4'

    try:
        # Define yt-dlp options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best video and audio, and merge them
            'merge_output_format': 'mp4',  # Ensure output is in MP4 format
            'outtmpl': outputFilePath,  # Save with title as filename
            'nocheckcertificate': True,  # Skip SSL certificate verification
        }

        # Use yt-dlp to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_url, download=True)
            video_title = info_dict.get('title', 'facebook_video')
            temp_video_path = os.path.join(outputFilePath)

        # Serve the video as a response
        with open(temp_video_path, 'rb') as video_file:
            response = HttpResponse(video_file, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(temp_video_path)}"'
            return response

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        # Clean up downloaded file
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)




@api_view(['POST'])
def download_youtube_video_url(request):
    """
    API to fetch the direct URL of a YouTube video.
    Accepts a POST request with the YouTube video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    youtube_url = request.data['url']

    cookies = request.COOKIES
    
    # Print the cookies to the console (this can also be logged for debugging)
    print("Cookies received:", cookies)

    # Validate URL
    YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    if not re.match(YOUTUBE_URL_REGEX, youtube_url):
        return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Get the best quality MP4 format
            'noplaylist': True,  # Ignore playlists
            'nocheckcertificate': True,  # Skip SSL certificate verification
            'cookies': cookies
        }

        # Extract video information without downloading
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_direct_url = info['url']  # Direct URL for playback/download

        # Return the video URL in the response
        return Response({'video_url': video_direct_url}, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the exception for debugging and return an error response
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
