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
def download_youtube_video_url(request):
    """
    API to fetch the direct URL of a YouTube video.
    Accepts a POST request with the YouTube video URL in the request body.
    """
    if 'url' not in request.data:
        return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    youtube_url = request.data['url']

    # Get cookies from request and prepare them for yt-dlp
    cookies = request.COOKIES

    # Print cookies for debugging (optional)
    print("Cookies received:", cookies)

    # Validate URL format using regular expression
    YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    if not re.match(YOUTUBE_URL_REGEX, youtube_url):
        return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Convert cookies to the format yt-dlp accepts (i.e., as a dictionary or cookies file)
        if cookies:
            # For example, you can create a cookies file or pass cookies as a dict
            cookie_dict = {key: value for key, value in cookies.items()}

            # Optionally, you can write cookies to a temporary file and pass the file path
            # with open('/path/to/cookies.txt', 'w') as cookie_file:
            #     json.dump(cookie_dict, cookie_file)

        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Get the best quality MP4 format
            'noplaylist': True,  # Ignore playlists
            'nocheckcertificate': True,  # Skip SSL certificate verification
            'cookies': cookie_dict,  # Pass cookies as a dictionary directly
            'u': 'rajkumar109w@gmail.com',
            'p': 'JAISHREERAM@123'
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
