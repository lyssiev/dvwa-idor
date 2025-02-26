from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Post
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, PrivacyForm, CommentForm
from django.http import HttpResponse, HttpResponseForbidden

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            response = redirect("home")

            # ✅ Only assign "moderator" role (no more admin role)
            role = "moderator" if user.is_staff else "user"

            print(f"🔍 Setting role cookie: {role}")  # Debugging output

            response.set_cookie("role", role)  # 🚨 Still vulnerable to modification

            return response
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")



def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    """🚨 Vulnerable Home View - Uses a cookie to determine role instead of Django's authentication"""
    profile = Profile.objects.get(user=request.user)

    role = request.COOKIES.get("role", "user")  # Default to "user"

    return render(request, "home.html", {"profile": profile, "role": role})


def feed_view(request):
    form = PostForm(request.POST or None)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("feed")

    # Get user's posts
    user_posts = Post.objects.filter(user=request.user)
    # Get posts from followed users
    followed_users = request.user.profile.follows.all()
    followed_posts = Post.objects.filter(user__profile__in=followed_users)
    
    # Combine and order posts by most recent
    all_posts = (user_posts | followed_posts).order_by("-created_at")

    print("Total posts:", all_posts.count())

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
    profiles = Profile.objects.exclude(user=request.user)  # Exclude logged-in user
    followed_profiles = request.user.profile.follows.all()  # Get who the logged-in user follows
    return render(request, "profile_list.html", {"profiles": profiles, "followed_profiles": followed_profiles})


def following(request, pk):
    profile = Profile.objects.get(pk=pk)
    following = profile.follows.all()
    return render(request, "following.html", {"profile": profile, "following": following})

def followers(request, pk):
    profile = Profile.objects.get(pk=pk)
    followers = profile.followed_by.all()
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

@login_required
def user_settings(request):
    privacy_form = PrivacyForm(instance=request.user.profile)

    if request.method == "POST":
        privacy_form = PrivacyForm(request.POST, instance=request.user.profile)
        if privacy_form.is_valid():
            privacy_form.save()
            messages.success(request, "Your privacy settings have been updated!")
            return redirect("user_settings")

    return render(request, "settings.html", {"privacy_form": privacy_form})

@login_required
def post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()  # ✅ Initialize the form for GET requests

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            user_id = request.POST.get("user_id")  # 🔴 No validation! Attacker can modify this.
            user = get_object_or_404(User, id=user_id)  # Trusting the input (BAD)

            comment = comment_form.save(commit=False)
            comment.user = user  # 🔴 Setting user based on manipulated input
            comment.post = post
            comment.save()
            return redirect("post", post_id=post.id)

    return render(request, "post.html", {"post": post, "comments": comments, "comment_form": comment_form})

# moderator views

@login_required
def moderator_dashboard(request):
    """🚨 Vulnerable Moderator Dashboard - Uses a cookie instead of Django authentication"""
    role = request.COOKIES.get("role", "user")

    if role != "moderator":
        return HttpResponseForbidden("Access Denied - Only Moderators Allowed!")

    posts = Post.objects.all()
    users = Profile.objects.all()

    return render(request, "moderator_dashboard.html", {"posts": posts, "users": users})

@login_required
def edit_user(request, user_id):
    """🚨 Vulnerable Moderator Action - Uses cookie-based authentication"""
    role = request.COOKIES.get("role", "user")  # ❌ Attackers can modify this!

    if role != "moderator":
        return HttpResponseForbidden("❌ You do not have permission to edit users.")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        new_username = request.POST.get("new_username")
        if new_username:
            user.username = new_username
            user.save()

    return redirect("moderator_dashboard")


@login_required
def delete_post(request, post_id):
    """🚨 Vulnerable Moderator Action - Uses cookie-based authentication to allow post deletion"""
    role = request.COOKIES.get("role", "user")  # ❌ Attackers can modify this!

    if role != "moderator":
        return HttpResponseForbidden("❌ You do not have permission to delete posts.")

    post = get_object_or_404(Post, id=post_id)
    post.delete()
    
    return redirect("moderator_dashboard")

def disclaimer(request):
    return render(request, 'disclaimer.html')

def introduction(request):
    return render(request, 'introduction.html')