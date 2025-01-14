# Generated by Django 5.0.1 on 2024-03-22 05:27

import datetime
import django.db.models.deletion
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogCategoryModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category", models.CharField(max_length=80)),
            ],
            options={
                "verbose_name_plural": "Blog Category",
            },
        ),
        migrations.CreateModel(
            name="ExternalPostModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[("news", "News"), ("ceo", "CEO")], max_length=10
                    ),
                ),
                ("url", models.URLField()),
                ("image", models.FileField(blank=True, null=True, upload_to="blog/")),
                ("logo", models.FileField(blank=True, null=True, upload_to="blog/")),
                ("title", models.CharField(max_length=100)),
                ("views", models.IntegerField(blank=True, default=0)),
                ("date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="PostedSiteModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("posted_site", models.CharField(max_length=100)),
                ("site_url", models.URLField()),
                (
                    "site_logo",
                    models.ImageField(blank=True, null=True, upload_to="blog/"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Posted Site",
            },
        ),
        migrations.CreateModel(
            name="SubscriptionModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("source", models.CharField(blank=True, max_length=255, null=True)),
                ("activated", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="BlogSubCategoryModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sub_category", models.CharField(max_length=80)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sub_category",
                        to="Blog.blogcategorymodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Blog Sub Category",
            },
        ),
        migrations.CreateModel(
            name="FilterOptionModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("filter_name", models.CharField(max_length=80)),
                (
                    "sub_category",
                    models.ManyToManyField(
                        blank=True,
                        related_name="filter_subcategory",
                        to="Blog.blogsubcategorymodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Blog Filter Option",
            },
        ),
        migrations.AddField(
            model_name="blogcategorymodel",
            name="posted_site",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="site_category",
                to="Blog.postedsitemodel",
            ),
        ),
        migrations.CreateModel(
            name="PostModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "post_url",
                    models.CharField(max_length=255, unique=True, verbose_name="URL"),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "short_description",
                    models.TextField(blank=True, max_length=255, null=True),
                ),
                (
                    "feature_image",
                    models.FileField(blank=True, null=True, upload_to="blog/"),
                ),
                (
                    "feature_image_title",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "feature_image_alt_text",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "reading_time",
                    models.DurationField(default=datetime.timedelta(seconds=180)),
                ),
                (
                    "comment_option",
                    models.CharField(
                        choices=[
                            ("disabled", "Disable Comments"),
                            ("enabled", "Enable Comments"),
                        ],
                        default="disabled",
                        max_length=100,
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("total_view", models.IntegerField(blank=True, default=0)),
                ("keywords", models.CharField(blank=True, max_length=255, null=True)),
                ("schema_data", models.JSONField(blank=True, null=True)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Author",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_category",
                        to="Blog.blogcategorymodel",
                    ),
                ),
                (
                    "filter_option",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_filter",
                        to="Blog.filteroptionmodel",
                    ),
                ),
                (
                    "posted_sites",
                    models.ManyToManyField(
                        related_name="posts",
                        to="Blog.postedsitemodel",
                        verbose_name="Posted Sites",
                    ),
                ),
                (
                    "sub_categories",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_sub_category",
                        to="Blog.blogsubcategorymodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Posts",
            },
        ),
        migrations.CreateModel(
            name="PostedSiteTrackingModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_view", models.IntegerField(blank=True, default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "posted_site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="site_tracking",
                        to="Blog.postedsitemodel",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_tracking",
                        to="Blog.postmodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Posted Site Tracking",
            },
        ),
        migrations.CreateModel(
            name="PostContentModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", tinymce.models.HTMLField()),
                ("image", models.FileField(blank=True, null=True, upload_to="blog/")),
                ("video", models.URLField(blank=True, null=True)),
                (
                    "tracking",
                    models.CharField(
                        choices=[
                            ("below_content", "Below Content"),
                            ("above_content", "Above Content"),
                            ("below_header", "Below Header"),
                        ],
                        default="below_content",
                        max_length=100,
                    ),
                ),
                (
                    "alignment",
                    models.CharField(
                        choices=[
                            ("left", "Left"),
                            ("right", "Right"),
                            ("center", "Center"),
                            ("justify", "Justify"),
                        ],
                        default="center",
                        max_length=100,
                    ),
                ),
                ("padding_top", models.IntegerField(default=0)),
                ("padding_bottom", models.IntegerField(default=0)),
                ("padding_left", models.IntegerField(default=0)),
                ("padding_right", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_content",
                        to="Blog.postmodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Post Content",
            },
        ),
        migrations.CreateModel(
            name="CommentModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comment", models.TextField(max_length=255, verbose_name="Comment")),
                ("comment_date", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comment_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comment_post",
                        to="Blog.postmodel",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReadingListModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("added_on", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("read", "Read"), ("unread", "Unread")],
                        default="unread",
                        max_length=255,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reading_list_post",
                        to="Blog.postmodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reading_list_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TableofContentModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("link", models.CharField(blank=True, max_length=255, null=True)),
                ("activated", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_table_of_content",
                        to="Blog.postmodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Table of Content",
            },
        ),
    ]
