# Generated by Django 4.1.7 on 2023-04-02 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("purchase", "0014_alter_basket_payment_method"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="image",
        ),
        migrations.AddField(
            model_name="product",
            name="initials",
            field=models.CharField(default="", max_length=10, verbose_name="initials"),
            preserve_default=False,
        ),
    ]
