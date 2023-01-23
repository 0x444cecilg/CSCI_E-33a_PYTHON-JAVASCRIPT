import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from django import forms
from django.forms import ModelForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Posting, Follow
from .helpers import paginate


class PostingForm(ModelForm):
    class Meta:
        model = Posting
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }


def index(request):
    postings = Posting.objects.all().order_by('-date')
    posts = paginate(request, postings)
    
    # Creating a new post
    if request.method == "POST":
        form = PostingForm(request.POST)
        if form.is_valid():
            form.clean()
            new_post = form.save(commit=False)
            new_post.poster = request.user
            new_post = new_post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/index.html", {
                "form": form,
                "posts": posts,
                "session_user": request.user.id
            })
    else:
        return render(request, "network/index.html", {
            "form": PostingForm(),
            "posts": posts,
            "session_user": request.user.id
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    profile = User.objects.get(username=username)
    profile_pk = profile.id 
    date_joined = profile.date_joined
    postings = Posting.objects.filter(poster=profile_pk).order_by('-date')

    # Determine Follow status 
    followers = Follow.objects.filter(followee=profile_pk).count()
    followees = Follow.objects.filter(follower=profile_pk).count()
    if request.user.is_authenticated:
        follow_pair = Follow.objects.filter(follower=request.user, followee=profile_pk)
        follow_btn = "Unfollow" if follow_pair else "Follow"
    else:
        follow_btn = "None"

    # Determine whether current user is visiting his/her own profile
    follow_btn_disabled = (request.user == profile)

    if request.method == "POST":
        if follow_pair:
            follow_pair.delete()
            return HttpResponseRedirect(reverse("profile", args=(profile,)))
        else:
            new_follow_pair = Follow(follower=request.user, followee=profile)
            new_follow_pair.save()
            return HttpResponseRedirect(reverse("profile", args=(profile,)))
    else:
        return render(request, "network/profile.html", {
            "username": username,
            "postings": postings,
            "followers": followers,
            "followees": followees,
            "follow_btn": follow_btn,
            "follow_btn_disabled": follow_btn_disabled,
            "date_joined": date_joined,
            "session_user": request.user.id
        })


@login_required
def following(request):
    followees = set(Follow.objects.filter(follower=request.user).values_list())
    follow_list = []
    for item in followees:
        follow_list.append(item[2])

    postings = Posting.objects.filter(poster__id__in=follow_list).order_by('-date')
    posts = paginate(request, postings)

    return render(request, "network/following.html", {
        "posts": posts,
        "session_user": request.user.id
    })


@ensure_csrf_cookie
@login_required
def edit(request, post_id):
    
    # Query for requested post
    try:
        post = Posting.objects.get(pk=post_id)
    except Posting.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(post.serialize())
    elif request.method == "PUT":
        data = json.loads(request.body)
        post.content = data["content"]
        post.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@ensure_csrf_cookie
@login_required
def like(request, post_id):
    
    # Query for requested post
    try:
        post = Posting.objects.get(pk=post_id)
    except Posting.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    if request.method == "GET":
        return JsonResponse(post.serialize())
    elif request.method == 'PUT':
        data = json.loads(request.body)
        new_like = data["likes"]
        if str(request.user) in post.serialize()["likes"]: # Unlike a post 
            post.likes.remove(new_like)
            post.save()
        else: # Like a post
            post.likes.add(new_like) 
            post.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)