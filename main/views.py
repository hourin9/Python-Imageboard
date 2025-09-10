from django.http import HttpResponse;
from django.shortcuts import redirect, render

from main import forms

def index(request):
    print(type(request));
    return HttpResponse(b"hello world");

def upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

