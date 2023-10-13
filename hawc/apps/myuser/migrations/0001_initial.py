import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HAWCUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(unique=True, max_length=254, db_index=True),
                ),
                (
                    "first_name",
                    models.CharField(max_length=30, verbose_name="first name", blank=True),
                ),
                (
                    "last_name",
                    models.CharField(max_length=30, verbose_name="last name", blank=True),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Group",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Permission",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={"ordering": ("last_name",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "HERO_access",
                    models.BooleanField(
                        default=False,
                        help_text=b"All HERO links will redirect to the login-only HERO access page, allowing for full article text.",
                        verbose_name=b"HERO access",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        related_name="profile",
                        on_delete=models.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
