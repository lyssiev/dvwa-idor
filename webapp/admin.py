from django.contrib import admin
from .models import Profile, Post, Comment
from django.contrib.auth.models import User, Group

class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", "email", "is_staff"]
    list_display = ["username", "email", "is_staff"]
    list_filter = ["is_staff"]
    search_fields = ["username", "email"]
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Post)
admin.site.register(Comment)
