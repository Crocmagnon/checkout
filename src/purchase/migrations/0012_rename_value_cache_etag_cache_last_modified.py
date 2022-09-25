# Generated by Django 4.1.1 on 2022-09-25 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchase", "0011_rename_cacheetag_cache"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cache",
            old_name="value",
            new_name="etag",
        ),
        migrations.AddField(
            model_name="cache",
            name="last_modified",
            field=models.DateTimeField(auto_now=True),
        ),
    ]