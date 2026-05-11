from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm

from .models import User


class UserCreationFormEmail(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class UserChangeFormEmail(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        field_classes = {"password": ReadOnlyPasswordHashField}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationFormEmail
    form = UserChangeFormEmail
    list_display = ("email", "is_staff", "is_superuser")
    ordering = ("email",)
    search_fields = ("email",)
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
