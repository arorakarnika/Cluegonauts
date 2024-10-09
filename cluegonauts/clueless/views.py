from django.shortcuts import render

def index(request):
    return render(request, "clueless/index.html")

def gameb(request):
    return render(request, "clueless/gameb.html")
