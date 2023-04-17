from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post
from .forms import PostForm


@login_required
def index(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-timestamp')

    #pagination
    paginator_instance = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator_instance.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver first page
        posts = paginator_instance.page(1)
    except EmptyPage:
        #if page is out of range, deliver last page of results
        posts = paginator_instance.page(Paginator.num_pages)

    context = {'form': form, 'posts': posts}
    return render(request, "network/index.html", context)


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
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user_profile).order_by('-timestamp')

    #pagination
    paginator_instance = Paginator(posts, 10)
    page = request.GET.get('page')
    
    try:
        posts = paginator_instance.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver first page
        posts = paginator_instance.page(1) 
    except EmptyPage:
        #if page is out of range, deliver last page of results
        posts = paginator_instance.page(Paginator.num_pages)

    context = {
        'user_profile': user_profile,
        'posts': posts,
    }

    if request.method == "POST":
        action = request.POST["action"]
        if request.user != user_profile:
            if action == "Follow":
                request.user.following.add(user_profile)
                context["action"] = "Unfollow"
            elif action == "Unfollow":
                request.user.following.remove(user_profile)
                context["action"] = "Follow"
        return render(request, "network/profile.html", context)
    else:
        if request.user in user_profile.followers.all():
            context["action"] = "Unfollow"
        else:
            context["action"] = "Follow"

        return render(request, "network/profile.html", context)
    

@login_required
def following(request):
    # get the posts of the users that the current user is following
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')

    #pagination
    paginator_instance = Paginator(posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator_instance.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver first page
        posts = paginator_instance.page(1)
    except EmptyPage:
        #if page is out of range, deliver last page of results
        posts = paginator_instance.page(Paginator.num_pages)


    context = {'posts': posts}
    return render(request, "network/following.html", context)


@login_required
@csrf_exempt
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user:
        return (JsonResponse({"error": "You can only edit your own posts."}, status=403))
    
    if request.method == "POST":
        data = json.loads(request.body)
        post_content = data.get("content", "").strip()
        print(f"Received POST data: {data}")
        if post_content:
            post.content = post_content
            post.save()
            return JsonResponse({'content': post.content})
    return JsonResponse({"error": "Invalid Request"}, status=400)
    