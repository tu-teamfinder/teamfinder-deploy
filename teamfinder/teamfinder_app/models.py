from django.db import models

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=32)
    password = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    year = models.IntegerField()

class Group(models.Model):
    group_id = models.CharField(primary_key=True, max_length=32)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups") ##
    group_name = models.CharField(max_length=255)

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Message(models.Model):
    message_id = models.CharField(primary_key=True, max_length=32)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")

class DirectMessage(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, primary_key=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_direct_messages")

class GroupMessage(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_messages")

class Post(models.Model):
    post_id = models.CharField(primary_key=True, max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    heading = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class PostComment(models.Model):
    post_comment_id = models.CharField(primary_key=True, max_length=32)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    reaction = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ResultPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    tag = models.CharField(max_length=255)

class RecruitPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    tag = models.CharField(max_length=255)
    status = models.CharField(max_length=50)

class Requirement(models.Model):
    require_id = models.CharField(primary_key=True, max_length=32)
    post = models.ForeignKey(RecruitPost, on_delete=models.CASCADE, related_name="requirements")
    req_faculty = models.CharField(max_length=255)
    req_major = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField()

class Request(models.Model):
    request_id = models.CharField(primary_key=True, max_length=32)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    message = models.TextField()
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

class Registration(models.Model):
    registration_id = models.CharField(primary_key=True, max_length=32)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="registrations")
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
