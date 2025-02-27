from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import json

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # follows is a many-to-many relationship 
    follows = models.ManyToManyField( 
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True
    ) 
    private = models.BooleanField(default=False)
        
    def __str__(self):
        return self.user.username
    
    # Create a profile object for each new user
    def create_profile(sender, instance, created, **kwargs):
        if created:
            user_profile = Profile(user=instance)
            user_profile.save()
            user_profile.follows.set([instance.profile.id])
            user_profile.save()

    post_save.connect(create_profile, sender=User)

# Post model
class Post(models.Model):
    user = models.ForeignKey(
        User, related_name="posts", on_delete=models.DO_NOTHING
    )
    body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    # post information set
    def __str__(self):
        return (
            f"{self.user} "
            f"({self.created_at:%Y-%m-%d %H:%M}): "
            f"{self.body[:30]}..."
        )

# Comment model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    # comment information set
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"
    
# Progress model
class Progress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completed_exercises = models.TextField(default="[]")

    # get completed exercises from JSON
    def get_completed_exercises(self):
        try:
            return json.loads(self.completed_exercises)
        except json.JSONDecodeError:
            return []

    # add exercise to completed exercises
    def add_exercise(self, exercise_number):
        exercises = self.get_completed_exercises()
        if exercise_number not in exercises:
            exercises.append(exercise_number)
            self.completed_exercises = json.dumps(exercises)
            self.save()

    # calculate progress percentage
    def progress_percentage(self):
        total_exercises = 5 
        return (len(self.get_completed_exercises()) / total_exercises) * 100