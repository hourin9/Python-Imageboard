import os;
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

    poptags: set[models.Tag] = set();
    for artwork in page:
        for tag in artwork.tags.all():
            poptags.add(tag);

    return render(
        request,
        "list.html",
        {"page": page, "popular_tags": poptags}
    );

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

def artwork_upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

def artwork_update(request, pk):
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    if request.method == "POST":
        form = forms.ImagePost(request.POST, instance=artwork);
        if form.is_valid():
            form.save();
            return redirect("imageview", pk=artwork.pk);
    else:
        form = forms.ImageUpdate(instance=artwork);
    return render(request, "imageupdate.html", {"form": form, "artwork": artwork});

def artwork_delete(request, pk):
    del request;
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    if artwork and os.path.isfile(artwork.image.path):
        os.remove(artwork.image.path);
    artwork.delete();
    return redirect("index");

