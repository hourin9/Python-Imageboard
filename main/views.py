from django.http import HttpResponse;
from django.shortcuts import get_object_or_404, redirect, render;
from django.core.paginator import Paginator;

from main import forms, models

def index(request):
    tag_query = request.GET.get("q");
    posts = models.Artwork.objects.all();

    if tag_query:
        tags = tag_query.split();
        for name in tags:
            posts = posts.filter(tags__name__iexact=name);

    posts = posts.order_by("-uploadt");
    paginator = Paginator(posts, 20);
    pagen = request.GET.get("page");
    print("getting page ", pagen);
    page = paginator.get_page(pagen);

    return render(request, "list.html", {"page": page});

def imageview(request, pk):
    artwork = get_object_or_404(models.Artwork, pk=pk);
    return render(request, "imageview.html", {"artwork": artwork});

def tagcreate(request):
    if request.method == "POST":
        form = forms.TagCreation(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.TagCreation();
    return render(request, "tagcreate.html", {"form": form});

def tag_delete(request, pk):
    del request;
    tag = get_object_or_404(models.Tag, pk=pk);
    tag.delete();
    return redirect("index");

def upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

def delete_artwork(request, pk):
    del request;
    artwork = get_object_or_404(models.Artwork, pk=pk);
    artwork.delete();
    return redirect("index");

