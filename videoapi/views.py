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
import json

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

COOKIES_FILE_PATH = "cookies.txt"

@api_view(['POST'])
def download_youtube_video_url(request):
        if request.method == "POST":
            try:
                # Parse the request body
                body = json.loads(request.body)
                video_url = body.get("url")

                if not video_url:
                    return JsonResponse({"error": "Missing video_url"}, status=400)

                # Ensure the cookies file exists
                if not os.path.exists(COOKIES_FILE_PATH):
                    return JsonResponse({"error": "Cookies file not found"}, status=500)

                # yt-dlp options
                ydl_opts = {
                    "format": "best",
                    "cookiefile": COOKIES_FILE_PATH,  # Use centralized cookies file
                }

                # Extract the video URL
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=False)
                    absolute_url = info_dict.get("url")
                    video_title = info_dict.get("title")
                    thumbnail_url = info_dict.get("thumbnail")


                if not absolute_url:
                    return JsonResponse({"error": "Failed to retrieve video URL"}, status=500)

                return JsonResponse({
                    "absolute_url": absolute_url,
                    "title": video_title,
                    "thumbnail": thumbnail_url
                }, status=200)

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"error": "Invalid request method"}, status=405)


INSTAGRAM_COOKIES_FILE_PATH = "instagram-cookies.txt"

@api_view(['POST'])
def download_instagram_video_url(request):
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)
            video_url = body.get("url")

            if not video_url:
                return JsonResponse({"error": "Missing video_url"}, status=400)

            # Ensure the cookies file exists
            if not os.path.exists(INSTAGRAM_COOKIES_FILE_PATH):
                return JsonResponse({"error": "Cookies file not found"}, status=500)

            # yt-dlp options
            ydl_opts = {
                "format": "best",
                "cookiefile": INSTAGRAM_COOKIES_FILE_PATH,  # Use centralized cookies file
            }

            # Extract the video URL
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                absolute_url = info_dict.get("url")
                video_title = info_dict.get("title")
                thumbnail_url = info_dict.get("thumbnail")


            if not absolute_url:
                return JsonResponse({"error": "Failed to retrieve video URL"}, status=500)

            return JsonResponse({
                "absolute_url": absolute_url,
                "title": video_title,
                "thumbnail": thumbnail_url
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



FACEBOOK_COOKIES_FILE_PATH = "facebook-cookies.txt"

@api_view(['POST'])
def download_facebook_video_url(request):
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)
            video_url = body.get("url")

            if not video_url:
                return JsonResponse({"error": "Missing video_url"}, status=400)

            # Ensure the cookies file exists
            if not os.path.exists(FACEBOOK_COOKIES_FILE_PATH):
                return JsonResponse({"error": "Cookies file not found"}, status=500)

            # yt-dlp options for Facebook
            ydl_opts = {
                "format": "best",
                "cookiefile": FACEBOOK_COOKIES_FILE_PATH,  # Use centralized cookies file
            }

            # Extract the video URL
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                absolute_url = info_dict.get("url")
                video_title = info_dict.get("title")
                thumbnail_url = info_dict.get("thumbnail")

            if not absolute_url:
                return JsonResponse({"error": "Failed to retrieve video URL"}, status=500)

            return JsonResponse({
                "absolute_url": absolute_url,
                "title": video_title,
                "thumbnail": thumbnail_url
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
