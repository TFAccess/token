# Generated by Django 5.0.1 on 2024-03-22 12:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Blog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postedsitemodel",
            name="site_logo",
            field=models.FileField(blank=True, null=True, upload_to="blog/"),
        ),
    ]
