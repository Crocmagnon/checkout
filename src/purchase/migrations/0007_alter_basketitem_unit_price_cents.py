# Generated by Django 4.0.4 on 2022-04-27 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchase", "0006_basketitem_unit_price_cents"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basketitem",
            name="unit_price_cents",
            field=models.PositiveIntegerField(
                help_text="product's unit price in cents at the time of purchase",
                verbose_name="unit price (cents)",
            ),
        ),
    ]