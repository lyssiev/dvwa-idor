from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Post, Progress
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, PrivacyForm, CommentForm
from django.http import HttpResponseForbidden
import requests
import json
import base64
import hashlib

def login_view(request):
    """ Handles user login """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            response = redirect("home")

            role = "moderator" if user.is_staff else "user"

            response.set_cookie("role", role)  # vulnerable to cookie manipulation

            return response
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

def logout_view(request):
    """ Handles user logout """
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    """ Vulnerable Home View - Uses a SHA256-encoded cookie to determine role instead of Django's authentication """
    profile = Profile.objects.get(user=request.user)

    # Default role is "user", hashed with SHA256
    default_role_hashed = hashlib.sha256("user".encode()).hexdigest()
    hashed_role = request.COOKIES.get("role", default_role_hashed)

    # Try to decode the SHA256 role safely
    role = "user"  # Fallback to a safe default
    if hashed_role == hashlib.sha256("moderator".encode()).hexdigest():
        role = "moderator"

    flag_ex2 = None
    FLAG_API_URL = "https://api-dvwa.onrender.com/api/get_flag"

    # If the role is moderator, fetch the flag
    if role == "moderator":
        try:
            response = requests.post(FLAG_API_URL, json={"exercise": "2"})
            if response.status_code == 200:
                flag_ex2 = response.json().get("flag", None)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching flag: {e}")

    response = render(request, "home.html", {"profile": profile, "role": role, "flag_ex2": flag_ex2})

    # Ensure the cookie is always stored as SHA256 hash
    hashed_role = hashlib.sha256(role.encode()).hexdigest()
    response.set_cookie("role", hashed_role)

    return response

@login_required
def feed_view(request):
    """ Displays the user's feed with their posts and posts from followed users """
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
    """ Handles user registration """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "register.html")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

@login_required
def profile_list(request):
    """ Displays a list of profiles excluding the logged-in user """
    profiles = Profile.objects.exclude(user=request.user)  # Exclude logged-in user
    followed_profiles = request.user.profile.follows.all()  # Get who the logged-in user follows
    return render(request, "profile_list.html", {"profiles": profiles, "followed_profiles": followed_profiles})

@login_required
def following(request, pk):
    """ Displays the list of users that a specific profile is following """
    profile = Profile.objects.get(pk=pk)
    following = profile.follows.all()
    return render(request, "following.html", {"profile": profile, "following": following})

@login_required
def followers(request, pk):
    """ Displays the list of followers of a specific profile """
    profile = Profile.objects.get(pk=pk)
    followers = profile.followed_by.all()
    return render(request, "followers.html", {"profile": profile, "followers": followers})

@login_required
def profile(request, pk):
    """ Displays a specific user's profile and handles follow/unfollow actions """
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()

    profile = get_object_or_404(Profile, pk=pk)
    flag = None

    # If the profile is private and the logged-in user is not the profile owner and not following the profile, fetch the flag as the IDOR has been exploited
    if profile.private and request.user != profile.user and profile not in request.user.profile.follows.all():
        try:
            response = requests.post("https://api-dvwa.onrender.com/api/get_flag", json={"exercise": "1"})
            print(f"API Response: {response.status_code}")
            print(f"API Response: {response.json()}")
            if response.status_code == 200:
                flag = response.json().get("flag")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching flag: {e}")

    # Handle follow/unfollow actions
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    
    return render(request, "profile.html", {"profile": profile, "flag": flag})

@login_required
def user_settings(request):
    """ Handles updating user privacy settings """
    privacy_form = PrivacyForm(instance=request.user.profile)

    # Handle updating privacy settings
    if request.method == "POST":
        privacy_form = PrivacyForm(request.POST, instance=request.user.profile)
        if privacy_form.is_valid():
            privacy_form.save()
            messages.success(request, "Your privacy settings have been updated!")
            return redirect("user_settings")

    return render(request, "settings.html", {"privacy_form": privacy_form})

FLAG_API_URL = "https://api-dvwa.onrender.com/api/get_flag"

@login_required
def post_view(request, post_id):
    """ Displays a specific post and handles adding comments """
    post = get_object_or_404(Post, id=post_id)
    post_user_profile = post.user.profile

    # If the post is private and the logged-in user is not the post owner and not following the post owner, return 403 Forbidden (also a fix to exercise 1)
    if post_user_profile.private and request.user != post.user and post_user_profile not in request.user.profile.follows.all():
        return HttpResponseForbidden()
    comments = post.comments.all()
    comment_form = CommentForm()
    
    flag_ex3 = request.session.pop("flag_ex3", None)  # retrieve flag from session if set

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            user_id = request.POST.get("user_id")  # No validation so attacker can modify this.
            user = get_object_or_404(User, id=user_id)  # Trusting the input

            comment = comment_form.save(commit=False)
            comment.user = user # attacker can change user
            comment.post = post
            comment.save()

            if user_id and str(request.user.id) != user_id:
                try:
                    response = requests.post(FLAG_API_URL, json={"exercise": "3"})
                    if response.status_code == 200:
                        request.session["flag_ex3"] = response.json().get("flag", None) # store flag in session
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching flag: {e}")

            return redirect("post", post_id=post.id)
    return render(request, "post.html", {"post": post, "comments": comments, "comment_form": comment_form, "flag_ex3": flag_ex3})

@login_required
def moderator_dashboard(request):
    """ Displays the moderator dashboard with all posts and users """
    role = request.COOKIES.get("role", "user")

    if role != "cfde2ca5188afb7bdd0691c7bef887baba78b709aadde8e8c535329d5751e6fe": # Only Moderators Allowed
        return HttpResponseForbidden("Access Denied - Only Moderators Allowed!")

    posts = Post.objects.all()
    users = Profile.objects.all()

    return render(request, "moderator_dashboard.html", {"posts": posts, "users": users})

@login_required
def edit_user(request, user_id):
    """ Allows moderators to edit a user's username """
    role = request.COOKIES.get("role", "user")  # Attackers can modify this!

    if role != "cfde2ca5188afb7bdd0691c7bef887baba78b709aadde8e8c535329d5751e6fe": # Only Moderators Allowed
        return HttpResponseForbidden("You do not have permission to edit users.")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        new_username = request.POST.get("new_username")
        if new_username:
            user.username = new_username
            user.save()

    return redirect("moderator_dashboard")

@login_required
def delete_post(request, post_id):
    """ Allows moderators to delete a post """
    role = request.COOKIES.get("role", "user")  # Attackers can modify this!

    if role != "cfde2ca5188afb7bdd0691c7bef887baba78b709aadde8e8c535329d5751e6fe": # Only Moderators Allowed
        return HttpResponseForbidden(" You do not have permission to delete posts.")

    post = get_object_or_404(Post, id=post_id)
    post.delete()
    
    return redirect("moderator_dashboard")

def disclaimer(request):
    """ Renders the disclaimer page """
    return render(request, 'disclaimer.html')

def introduction(request):
    """ Renders the introduction page """
    return render(request, 'introduction.html')

@login_required
def update_progress(request):
    """ Updates the user's progress for an exercise """
    if request.method == "POST":
        progress, _ = Progress.objects.get_or_create(user=request.user)
        data = request.POST
        exercise_number = int(data.get("exercise"))
        if exercise_number not in progress.completed_exercises:
            progress.completed_exercises.append(exercise_number)
            progress.save()

        return JsonResponse({"completed_exercises": progress.completed_exercises})

@login_required
def get_progress(request):
    """ Retrieves the user's progress """
    progress, created = Progress.objects.get_or_create(user=request.user)
    return JsonResponse({
        "completed_exercises": progress.get_completed_exercises(),
        "progress": progress.progress_percentage()
    })

@login_required
def update_progress(request):
    """ Updates the user's progress for an exercise """
    if request.method == "POST":
        progress, created = Progress.objects.get_or_create(user=request.user)
        exercise_number = int(request.POST.get("exercise"))

        progress.add_exercise(exercise_number) 

        return JsonResponse({
            "completed_exercises": progress.get_completed_exercises(),
            "progress": progress.progress_percentage()
        })

@login_required
def reset_password_view(request):
    """ Resets a user's password and fetches a flag if the user is not the same as the one resetting the password """
    data = json.loads(request.body)
    user_id = data.get("user_id")
    new_password = data.get("new_password")

    # send a request to the api to reset the password
    flask_response = requests.post('http://127.0.0.1:5000/api/reset_password', json={
        "user_id": user_id,
        "new_password": new_password
    }).json()

    # Check if the user_id is a valid base64 encoded string
    try:
        decoded_user_id = base64.b64decode(user_id).decode('utf-8')
    except (TypeError, ValueError):
        return JsonResponse({"message": "Invalid user ID format.", "status": "error"})

    # get the flag for exercise 5 if the user is not the same as the one resetting the password
    flag_ex5 = None
    if str(request.user.id) != decoded_user_id:
        flag_response = requests.post("https://api-dvwa.onrender.com/api/get_flag", json={"exercise": "5"})
        if flag_response.status_code == 200:
            flag_ex5 = flag_response.json().get("flag")
        else:
            flag_ex5 = None
    else:
        flag_ex5 = None

    # return the flag from the api
    return JsonResponse({
        "message": flask_response.get("message"),
        "status": flask_response.get("status"),
        "flag": flag_ex5
    })

def solutions_view(request):
    """ Renders the solutions page """
    return render(request, "solutions.html")