# Generated by Django 4.1.1 on 2022-09-25 19:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("purchase", "0010_rename_basketitemetag_cacheetag"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CacheEtag",
            new_name="Cache",
        ),
    ]
