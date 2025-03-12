from django.urls import path, include
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('feed/', views.feed_view, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("profile_list/", views.profile_list, name="profile_list"),
    path('following/<int:pk>/', views.following, name='following'),
    path('followers/<int:pk>/', views.followers, name='followers'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path("post/<int:post_id>/", views.post_view, name="post"),
    path('settings/', views.user_settings, name='user_settings'),
    path("moderator_dashboard/", views.moderator_dashboard, name="moderator_dashboard"),
    path("delete_post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("edit_user/<int:user_id>/", views.edit_user, name="edit_user"),
    path('', views.disclaimer, name="disclaimer"),
    path("introduction/", views.introduction, name="intro"),
    path('get_progress/', views.get_progress, name='get_progress'),
    path('update_progress/', views.update_progress, name='update_progress'),
    path("reset_progress/", views.reset_progress, name="reset_progress"),
    path('reset_password_view/', views.reset_password_view, name='reset_password_view'),
    path("solutions/", views.solutions_view, name="solutions"),
]
