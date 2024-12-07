from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import * 

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email_address", "username", "name", "major", "faculty", "year", "is_staff", "is_active",)
    list_filter = ("username", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email_address", "password", "name", "major", "faculty", "year")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email_address", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions", "name",
                "major", "faculty", "year"
            )}
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)

admin.site.register(User, CustomUserAdmin)

model_list = [
    UserProfile,
    Faculty,
    FacultyTag,
    Major,
    MajorTag,
    Group,
    GroupMember,
    Message,
    DirectMessage,
    GroupMessage,
    Post,
    PostComment,
    ResultPost,
    RecruitPost,
    Requirement,
    Request,
    Team,
    TeamMember,
    Feedback,
]

for model in model_list:
    admin.site.register(model)