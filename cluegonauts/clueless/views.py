from django.shortcuts import render, render
from typing import List

from .classes import CharacterHandler

def index(request):
    char_handler = request.session.get("char_handler", None) if request.session.get("char_handler", None) else CharacterHandler()
    char_choices = char_handler.get_all_characters()
    return render(
        request, 
        "clueless/index.html", 
        char_choices=char_choices
        )

def gameb(request):
    return render(request, "clueless/gameb.html")
