from django.db import models
from django.contrib.auth.models import AbstractUser, User
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from django.contrib.auth.base_user import BaseUserManager
from teamfinder_app.validators import validate_file_size
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, UnidentifiedImageError
from cloudinary.models import CloudinaryField

class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(username, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=32)
    email_address = models.EmailField(blank=True)
    name = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = CloudinaryField('image', folder="images", blank=True, null=True, default="fallback.png", validators=[validate_file_size])
    bio = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.profile_image and not self.profile_image.closed:
            try:
                img = Image.open(self.profile_image)
                # Convert PNG with alpha to RGB before resizing
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

            except UnidentifiedImageError:
                raise ValueError("Invalid image uploaded")
            
            # Resize image if necessary
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)

                buffer = BytesIO()
                img.save(buffer, format='JPEG')  # Save as JPEG
                buffer.seek(0)

                self.profile_image = InMemoryUploadedFile(
                    buffer, 'ImageField', self.profile_image.name, 'image/jpeg', buffer.tell(), None
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Faculty(TagBase):
    faculty = models.TextField()

class FacultyTag(GenericTaggedItemBase):
    tag = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="faculty_tag")

class Major(TagBase):
    major = models.TextField()

class MajorTag(GenericTaggedItemBase):
    tag = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="major_tag")

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    heading = models.CharField(max_length=255)
    content = models.TextField()
    finish = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class PostComment(models.Model):
    post_comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    reaction = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ResultPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    tag = TaggableManager()

class RecruitPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    tag = TaggableManager()
    status = models.BooleanField(default=True)

class Requirement(models.Model):
    require_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(RecruitPost, on_delete=models.CASCADE, related_name="requirements")
    req_faculty = TaggableManager(through=FacultyTag)
    req_major = TaggableManager(through=MajorTag)
    year_min = models.IntegerField(default=1)
    year_max = models.IntegerField(default=4)
    description = models.TextField()

class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    message = models.TextField()
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    recruit_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedbacks')
    communication_pt = models.IntegerField()
    collaboration_pt = models.IntegerField()
    reliability_pt = models.IntegerField()
    technical_pt = models.IntegerField()
    empathy_pt = models.IntegerField()
    comment = models.TextField(blank=True)



    