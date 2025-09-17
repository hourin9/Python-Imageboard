from django.http import HttpResponse;
from django.shortcuts import redirect, render

from main import forms, models

def index(request):
    posts = models.Artwork.objects.order_by("-uploadt");
    return render(request, "list.html", {"posts": posts});

def tagcreate(request):
    if request.method == "POST":
        form = forms.TagCreation(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.TagCreation();
    return render(request, "tagcreate.html", {"form": form});

def upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

