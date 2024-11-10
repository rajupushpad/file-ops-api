from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def new_page(request):
    return HttpResponse("Welcome to the new page!")