import os;
from django.db.models.query import QuerySet
from django.http import HttpResponse;
from django.shortcuts import get_object_or_404, redirect, render;
from django.core.paginator import Paginator;

from django.contrib.auth import authenticate, login, logout;
from django.contrib.auth.decorators import login_required, user_passes_test;
from django.contrib.auth.models import User;

from main import forms, models

def mod_required(fn):
    return user_passes_test(lambda u: u.is_superuser, login_url="login")(fn)

def __handle_order_queries(
    what: str,
    posts: QuerySet[models.Artwork]) -> QuerySet:
    print("sorting by ", what);
    if what == "score":
        posts = posts.order_by("score");
    elif what == "score_asc":
        posts = posts.order_by("-score");
    elif what == "date_asc":
        posts = posts.order_by("uploadt");
    elif what == "date":
        posts = posts.order_by("-uploadt");
    else:
        posts = posts.order_by("-uploadt");
    return posts;

def index(request):
    tag_query = request.GET.get("q");
    posts: QuerySet[models.Artwork] = models.Artwork.objects.all();
    already_ordered: bool = False;

    if tag_query:
        tags = tag_query.split();
        for name in tags:
            if name[0] == '-':
                posts = posts.exclude(tags__name__iexact=name[1:]);
            elif name[0:5] == "order":
                posts = __handle_order_queries(name[6:], posts);
                already_ordered = True;
            else:
                posts = posts.filter(tags__name__iexact=name);

    if not already_ordered:
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

@login_required
def tagcreate(request):
    if request.method == "POST":
        form = forms.TagCreation(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.TagCreation();
    return render(request, "tagcreate.html", {"form": form});

@mod_required
def tag_delete(request, pk):
    del request;
    tag = get_object_or_404(models.Tag, pk=pk);
    tag.delete();
    return redirect("index");

@login_required
def artwork_upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            form.save();
            return redirect("index");
    form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

@login_required
def artwork_update(request, pk):
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    if request.method == "POST":
        form = forms.ImagePost(request.POST, instance=artwork);
        if form.is_valid():
            form.save();
            return redirect("imageview", pk=artwork.pk);
    else:
        form = forms.ImageUpdate(instance=artwork);
    return render(request, "imageupdate.html",
            {"form": form, "artwork": artwork});

@login_required
def artwork_delete(request, pk):
    del request;
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    if artwork and os.path.isfile(artwork.image.path):
        os.remove(artwork.image.path);
    artwork.delete();
    return redirect("index");

def logout_page(request):
    logout(request);
    return redirect("index");

def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username");
        password = request.POST.get("password");

        user = User.objects.filter(username=username);
        if user.exists():
            return redirect("register");

        user = User.objects.create_user(
            username=username
        );

        user.set_password(password);
        user.save();

        uauth = authenticate(
            username=username,
            password=password);
        if uauth is not None:
            login(request, uauth);
            return redirect("index");
        redirect("login");

    return render(request, "register.html");

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username");
        password = request.POST.get("password");

        if not User.objects.filter(username=username):
            return redirect("login");

        user = authenticate(
            username=username,
            password=password);
        if user is None:
            return redirect("login");
        else:
            login(request, user);
            return redirect("index");

    return render(request, "login.html");

