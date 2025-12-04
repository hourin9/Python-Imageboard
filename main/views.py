import os;
from django.db.models.query import QuerySet
from django.db.models import Sum;
from django.db.transaction import commit
from django.http import HttpResponse;
from django.shortcuts import get_object_or_404, redirect, render;
from django.core.paginator import Paginator;

from django.contrib.auth import authenticate, get_user, login, logout;
from django.contrib.auth.decorators import login_required, user_passes_test;
from django.contrib.auth.models import User
from django.urls import reverse;

from main import forms, models

def mod_required(fn):
    return user_passes_test(lambda u: u.is_superuser, login_url="login")(fn)

def __handle_order_queries(
    what: str,
    posts: QuerySet[models.Artwork]) -> QuerySet:
    print("sorting by ", what);
    if what == "score":
        posts = posts.order_by("-score");
    elif what == "score_asc":
        posts = posts.order_by("score");
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
            elif name.startswith("order:"):
                posts = __handle_order_queries(name[6:], posts);
                already_ordered = True;
            elif name.startswith("uploader:"):
                username = name[9:];
                posts = posts.filter(uploader__username__iexact=username);
            else:
                posts = posts.filter(tags__name__iexact=name);

    if not already_ordered:
        posts = posts.order_by("-uploadt");
    paginator = Paginator(posts, 20);
    pagen = request.GET.get("page");
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

def tag_list(request):
    q = request.GET.get("q", "").strip()
    tags = models.Tag.objects.all()

    if q:
        tags = tags.filter(name__icontains=q)

    tags = tags.order_by("name")

    return render(request, "taglist.html", {
        "tags": tags,
        "query": q,
    })

def user_page(request, username):
    user = get_object_or_404(User, username=username)

    uploaded = models.Artwork.objects.filter(uploader=user).order_by("-uploadt")[:5]

    upvoted = models.Artwork.objects.filter(
        votes__user=user,
        votes__vtype=models.ArtworkVote.Type.UPVOTE,
    ).distinct()[:5]

    ctx = {
        "profile": user,
        "uploaded": uploaded,
        "upvoted": upvoted,
    }

    return render(request, "user.html", ctx)

@login_required
def artwork_upload(request):
    if request.method == "POST":
        form = forms.ImagePost(request.POST, request.FILES);
        if form.is_valid():
            artwork = form.save(commit=False);
            artwork.uploader = request.user;
            artwork.save();
            form.save(commit=True);
            return redirect("index");
    else:
        form = forms.ImagePost();
    return render(request, "upload.html", {"form": form});

@login_required
def artwork_update(request, pk):
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    if request.method == "POST":
        form = forms.ImagePost(request.POST, instance=artwork);
        if form.is_valid():
            form.save(commit=True);
            return redirect("imageview", pk=artwork.pk);
    else:
        initial_tags = " ".join(t.name for t in artwork.tags.all());
        form = forms.ImageUpdate(instance=artwork, initial={"tags": initial_tags});
    return render(request, "imageupdate.html",
            {"form": form, "artwork": artwork});

@login_required
def artwork_rmvote(request, pk):
    artwork = get_object_or_404(models.Artwork, pk=pk);
    user = request.user;
    vote = models.ArtworkVote.objects \
        .filter(artwork=artwork, user=user) \
        .first();

    if vote:
        vote.delete();

        total = artwork.votes.aggregate(Sum('vtype'))['vtype__sum'] or 0;
        artwork.score = total;
        artwork.save(update_fields=['score']);

    q = request.GET.get('q', '')
    redirect_url = reverse('imageview', args=[pk])
    if q:
        redirect_url += f'?q={q}'

    return redirect(redirect_url);

@login_required
def artwork_upvote(request, pk):
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    user = request.user;
    print(f"{user.username} {user.user_permissions}");

    vote, created = models.ArtworkVote.objects.get_or_create(
        artwork=artwork,
        user=user,
        defaults={'vtype': models.ArtworkVote.Type.UPVOTE}
    );

    if not created and vote.vtype == models.ArtworkVote.Type.UPVOTE:
        vote.delete();

    elif not created and vote.vtype != models.ArtworkVote.Type.UPVOTE:
        vote.vtype = models.ArtworkVote.Type.UPVOTE;
        vote.save();

    total = artwork.votes.aggregate(Sum('vtype'))['vtype__sum'] or 0;
    artwork.score = total;
    artwork.save(update_fields=['score']);

    q = request.GET.get('q', '')
    redirect_url = reverse('imageview', args=[pk])
    if q:
        redirect_url += f'?q={q}'

    return redirect(redirect_url);

@login_required
def artwork_downvote(request, pk):
    artwork: models.Artwork = get_object_or_404(models.Artwork, pk=pk);
    user = request.user;
    print(f"{user.username} {user.user_permissions}");

    vote, created = models.ArtworkVote.objects.get_or_create(
        artwork=artwork,
        user=user,
        defaults={'vtype': models.ArtworkVote.Type.DOWNVOTE}
    );

    if not created and vote.vtype == models.ArtworkVote.Type.DOWNVOTE:
        vote.delete();

    elif not created and vote.vtype != models.ArtworkVote.Type.DOWNVOTE:
        vote.vtype = models.ArtworkVote.Type.DOWNVOTE;
        vote.save();

    total = artwork.votes.aggregate(Sum('vtype'))['vtype__sum'] or 0;
    artwork.score = total;
    artwork.save(update_fields=['score']);

    q = request.GET.get('q', '')
    redirect_url = reverse('imageview', args=[pk])
    if q:
        redirect_url += f'?q={q}'

    return redirect(redirect_url);


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

