from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('feed/', views.feed_view, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("profile_list/", views.profile_list, name="profile_list"),
    path('following/<int:pk>/', views.following, name='following'),
    path('followers/<int:pk>/', views.followers, name='followers'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path("post/<int:post_id>/", views.post_view, name="post"),
    path('settings/', views.user_settings, name='user_settings')
]
