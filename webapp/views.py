from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Post
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'home.html', {'profile': profile})

def feed_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("feed")
    form = PostForm()
    
    # Get user's posts
    user_posts = Post.objects.filter(user=request.user)
    # Get posts from followed users
    followed_users = request.user.profile.follows.all()
    followed_posts = Post.objects.filter(user__profile__in=followed_users)
    # Combine 
    all_posts = user_posts | followed_posts
    all_posts = all_posts.order_by("-created_at") 

    return render(request, "feed.html", {"form": form, "all_posts": all_posts})

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "profile_list.html", {"profiles": profiles})

def following(request, pk):
    profile = Profile.objects.get(pk=pk)
    following = profile.follows.all()
    return render(request, "following.html", {"profile": profile, "following": following})

def followers(request, pk):
    profile = Profile.objects.get(pk=pk)
    followers = profile.follows.all()
    return render(request, "followers.html", {"profile": profile, "followers": followers})

def profile(request, pk):
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()

    profile = Profile.objects.get(pk=pk)
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    return render(request, "profile.html", {"profile": profile})

